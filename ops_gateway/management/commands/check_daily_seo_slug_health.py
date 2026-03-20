from __future__ import annotations

import json
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from game_article.models import Article
from game_page.models import GamePage
from ops_gateway.models import DailyRobotRun
from seo_automation.models import SeoArticle


def _to_list(value) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def _post_alert_webhook(url: str, message: str, timeout_sec: int = 10) -> tuple[bool, str]:
    normalized = str(url or "").strip().lower()
    is_feishu = any(token in normalized for token in ["feishu.cn", "larksuite.com", "open.feishu.cn"])         or "/open-apis/bot/v2/hook/" in normalized

    if is_feishu:
        payload = {"msg_type": "text", "content": {"text": message}}
    else:
        payload = {"msgtype": "text", "text": {"content": message}}

    try:
        response = requests.post(url, json=payload, timeout=timeout_sec)
    except requests.RequestException as exc:
        return False, str(exc)

    if response.status_code >= 400:
        return False, f"http {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        data = {}

    if isinstance(data, dict):
        if is_feishu:
            status_code = data.get("StatusCode")
            code = data.get("code")
            if status_code not in (None, 0) and code not in (None, 0, "0"):
                return False, f"status_code={status_code} code={code} msg={data.get('StatusMessage') or data.get('msg')}"
        else:
            errcode = data.get("errcode")
            if errcode not in (None, 0, "0"):
                return False, f"errcode={errcode} errmsg={data.get('errmsg')}"
    return True, "ok"


def _resolve_audit_date(value: str | None):
    if value:
        return datetime.strptime(value, "%Y-%m-%d").date()

    tz_name = str(getattr(settings, "TIME_ZONE", "Asia/Shanghai") or "Asia/Shanghai")
    try:
        tzinfo = ZoneInfo(tz_name)
    except Exception:
        tzinfo = ZoneInfo("Asia/Shanghai")
    return datetime.now(tz=tzinfo).date()


def _safe_ratio(total: int, good: int) -> float:
    if total <= 0:
        return 1.0
    return round(float(good) / float(total), 4)


class Command(BaseCommand):
    help = "Audit daily SEO slug compliance for published game pages and articles."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            default="",
            help="Audit date in YYYY-MM-DD. Default: today in settings.TIME_ZONE.",
        )
        parser.add_argument(
            "--min-articles",
            type=int,
            default=None,
            help="Override minimum expected published article count for the day.",
        )
        parser.add_argument(
            "--min-games",
            type=int,
            default=None,
            help="Override minimum expected published game page count for the day.",
        )
        parser.add_argument(
            "--skip-run-check",
            action="store_true",
            help="Skip checking ops_gateway DailyRobotRun status.",
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output report as JSON.",
        )

    def handle(self, *args, **options):
        audit_date = _resolve_audit_date(options.get("date") or "")
        min_articles = options.get("min_articles")
        min_games = options.get("min_games")
        if min_articles is None:
            min_articles = int(getattr(settings, "SEO_SLUG_AUDIT_MIN_ARTICLES", 1))
        if min_games is None:
            min_games = int(getattr(settings, "SEO_SLUG_AUDIT_MIN_GAMES", 1))
        min_articles = max(0, int(min_articles))
        min_games = max(0, int(min_games))

        run_key = str(getattr(settings, "SEO_SLUG_AUDIT_RUN_KEY", "daily_full_cycle") or "daily_full_cycle")
        require_daily_run = bool(getattr(settings, "SEO_SLUG_AUDIT_REQUIRE_DAILY_RUN", True)) and not bool(
            options.get("skip_run_check")
        )

        article_qs = Article.objects.filter(status="published", published_at__date=audit_date)
        game_qs = GamePage.objects.filter(status="published", published_at__date=audit_date)
        seo_published_qs = SeoArticle.objects.filter(
            status="published",
            published_at__date=audit_date,
            published_article__isnull=False,
        )

        article_total = article_qs.count()
        article_slug_missing = article_qs.filter(Q(slug__isnull=True) | Q(slug="")).count()
        article_slug_ok = article_total - article_slug_missing

        game_total = game_qs.count()
        game_slug_missing = game_qs.filter(Q(slug__isnull=True) | Q(slug="")).count()
        game_slug_ok = game_total - game_slug_missing

        seo_published_total = seo_published_qs.count()
        seo_linked_slug_missing = seo_published_qs.filter(
            Q(published_article__slug__isnull=True) | Q(published_article__slug="")
        ).count()

        run = (
            DailyRobotRun.objects.filter(run_key=run_key, run_date=audit_date)
            .order_by("-started_at", "-id")
            .first()
        )

        anomalies: list[str] = []
        if require_daily_run:
            if run is None:
                anomalies.append("daily_run_missing")
            elif run.status not in {DailyRobotRun.STATUS_COMPLETED, DailyRobotRun.STATUS_PARTIAL}:
                anomalies.append(f"daily_run_status_{run.status}")

        if article_total < min_articles:
            anomalies.append("article_count_below_min")
        if game_total < min_games:
            anomalies.append("game_count_below_min")
        if article_slug_missing > 0:
            anomalies.append("article_slug_missing")
        if game_slug_missing > 0:
            anomalies.append("game_slug_missing")
        if seo_linked_slug_missing > 0:
            anomalies.append("seo_linked_article_slug_missing")

        report = {
            "audit_date": audit_date.isoformat(),
            "ok": len(anomalies) == 0,
            "anomalies": anomalies,
            "min_expected": {
                "articles": min_articles,
                "games": min_games,
            },
            "daily_run": {
                "run_key": run_key,
                "required": require_daily_run,
                "found": bool(run),
                "status": getattr(run, "status", ""),
                "error_message": (getattr(run, "error_message", "") or "")[:300],
            },
            "articles": {
                "published": article_total,
                "slug_ok": article_slug_ok,
                "slug_missing": article_slug_missing,
                "slug_ok_ratio": _safe_ratio(article_total, article_slug_ok),
            },
            "games": {
                "published": game_total,
                "slug_ok": game_slug_ok,
                "slug_missing": game_slug_missing,
                "slug_ok_ratio": _safe_ratio(game_total, game_slug_ok),
            },
            "seo_published": {
                "rows": seo_published_total,
                "linked_article_slug_missing": seo_linked_slug_missing,
                "linked_article_slug_ok": seo_published_total - seo_linked_slug_missing,
                "linked_article_slug_ok_ratio": _safe_ratio(
                    seo_published_total, seo_published_total - seo_linked_slug_missing
                ),
            },
        }

        if options.get("json"):
            self.stdout.write(json.dumps(report, ensure_ascii=False, sort_keys=True))
        else:
            self.stdout.write(
                f"[seo-slug-audit] date={report['audit_date']} ok={report['ok']} anomalies={','.join(anomalies) or 'none'}"
            )
            self.stdout.write(
                f"[articles] published={article_total} slug_missing={article_slug_missing} min_expected={min_articles}"
            )
            self.stdout.write(
                f"[games] published={game_total} slug_missing={game_slug_missing} min_expected={min_games}"
            )
            self.stdout.write(
                f"[seo_published] rows={seo_published_total} linked_article_slug_missing={seo_linked_slug_missing}"
            )

        if report["ok"]:
            self.stdout.write(self.style.SUCCESS("[ok] daily SEO slug audit passed"))
            return

        webhook_urls = _to_list(getattr(settings, "SEO_SLUG_AUDIT_ALERT_WEBHOOKS", []))
        email_receivers = _to_list(getattr(settings, "SEO_SLUG_AUDIT_ALERT_EMAILS", []))
        timeout_sec = max(5, int(getattr(settings, "CHARGEX_TIMEOUT_SEC", 15)))

        alert_message = (
            f"[SEO Slug Audit Alert] date={report['audit_date']} anomalies={','.join(anomalies)} "
            f"articles={article_total}/{min_articles} games={game_total}/{min_games} "
            f"article_slug_missing={article_slug_missing} game_slug_missing={game_slug_missing} "
            f"seo_linked_slug_missing={seo_linked_slug_missing} run_status={report['daily_run']['status'] or 'none'}"
        )
        alert_subject = f"[SEO] Daily slug audit alert ({report['audit_date']})"

        webhook_ok = 0
        webhook_failed = 0
        for url in webhook_urls:
            success, detail = _post_alert_webhook(url, alert_message, timeout_sec=timeout_sec)
            if success:
                webhook_ok += 1
            else:
                webhook_failed += 1
                self.stderr.write(self.style.WARNING(f"[warn] webhook failed {url}: {detail}"))

        email_ok = 0
        if email_receivers:
            try:
                send_mail(
                    subject=alert_subject,
                    message=alert_message,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", ""),
                    recipient_list=email_receivers,
                    fail_silently=False,
                )
                email_ok = len(email_receivers)
            except Exception as exc:
                self.stderr.write(self.style.WARNING(f"[warn] email alert failed: {exc}"))

        self.stderr.write(
            self.style.WARNING(
                f"[alerted] webhook_ok={webhook_ok} webhook_failed={webhook_failed} email_ok={email_ok}"
            )
        )
        raise CommandError(f"daily SEO slug audit failed: {','.join(anomalies)}")
