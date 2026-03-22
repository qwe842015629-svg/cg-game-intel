from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.utils import timezone
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import DailyRobotConfig, OperationApproval
from .security import get_client_ip, verify_hmac_signature
from .serializers import (
    ApprovalDecisionSerializer,
    ApprovalExecuteSerializer,
    AutomationGooglePlayImportSerializer,
    AutomationPublishedReviewSerializer,
    AutomationSeoDailyRunSerializer,
    CreatePublishRequestSerializer,
    DailyRobotConfigSerializer,
    OperationAuditLogSerializer,
    OperationApprovalSerializer,
)
from .services import (
    create_audit_log,
    execute_approval,
    mark_approval_executed,
    mark_approval_failed,
    run_google_play_import_automation,
    run_published_article_recheck_automation,
    run_seo_daily_automation,
)


class AdminOnlyAPIView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAdminUser]


class CreatePublishRequestAPIView(APIView):
    """
    Create approval request for publishing SEO article.

    Access policy:
    - Admin users (session/token)
    - or trusted signed client (HMAC)
    """

    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        is_admin = bool(getattr(request.user, "is_authenticated", False) and request.user.is_staff)
        client_id = ""
        if not is_admin:
            verified, client_id, err = verify_hmac_signature(request)
            if not verified:
                return Response({"detail": err}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreatePublishRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        idempotency_key = (data.get("idempotency_key") or "").strip()
        existing = None
        if idempotency_key:
            existing = (
                OperationApproval.objects.filter(
                    action=OperationApproval.ACTION_SEO_ARTICLE_PUBLISH,
                    idempotency_key=idempotency_key,
                )
                .exclude(status=OperationApproval.STATUS_REJECTED)
                .order_by("-requested_at")
                .first()
            )
        if existing:
            output = OperationApprovalSerializer(existing).data
            output["_idempotent_reuse"] = True
            return Response(output, status=status.HTTP_200_OK)

        seo_article_id = data["seo_article_id"]
        payload = {
            "seo_article_id": seo_article_id,
            "publish_now": bool(data.get("publish_now", False)),
            "run_step5": bool(data.get("run_step5", True)),
            "publish_at": data.get("publish_at") or "",
        }
        approval = OperationApproval.objects.create(
            action=OperationApproval.ACTION_SEO_ARTICLE_PUBLISH,
            target_type="seo_article",
            target_id=str(seo_article_id),
            payload=payload,
            status=OperationApproval.STATUS_PENDING,
            risk_level=int(data.get("risk_level") or 3),
            reason=data.get("reason", ""),
            idempotency_key=idempotency_key,
            requested_by=request.user if is_admin else None,
            client_id=client_id,
            client_ip=get_client_ip(request),
        )
        create_audit_log(
            approval=approval,
            event_type="request_created",
            actor=request.user if is_admin else None,
            client_id=approval.client_id,
            client_ip=approval.client_ip,
            request_snapshot=payload,
            result_snapshot={"status": approval.status},
            message="鍒涘缓鍙戝竷瀹℃壒鐢宠",
        )
        return Response(OperationApprovalSerializer(approval).data, status=status.HTTP_201_CREATED)


class ApprovalListAPIView(AdminOnlyAPIView):
    def get(self, request):
        queryset = OperationApproval.objects.all().order_by("-requested_at")
        status_q = (request.query_params.get("status") or "").strip()
        action_q = (request.query_params.get("action") or "").strip()
        q = (request.query_params.get("q") or "").strip()

        if status_q:
            queryset = queryset.filter(status=status_q)
        if action_q:
            queryset = queryset.filter(action=action_q)
        if q:
            queryset = queryset.filter(
                Q(target_id__icontains=q)
                | Q(idempotency_key__icontains=q)
                | Q(reason__icontains=q)
                | Q(error_message__icontains=q)
            )

        limit = request.query_params.get("limit")
        if limit:
            try:
                n = max(1, min(200, int(limit)))
                queryset = queryset[:n]
            except Exception:
                pass

        data = OperationApprovalSerializer(queryset, many=True).data
        return Response({"count": len(data), "results": data}, status=status.HTTP_200_OK)


class ApprovalDetailAPIView(AdminOnlyAPIView):
    def get(self, request, request_id):
        approval = OperationApproval.objects.filter(request_id=request_id).first()
        if not approval:
            return Response({"detail": "瀹℃壒鍗曚笉瀛樺湪"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OperationApprovalSerializer(approval).data, status=status.HTTP_200_OK)


class ApprovalApproveAPIView(AdminOnlyAPIView):
    def post(self, request, request_id):
        approval = OperationApproval.objects.filter(request_id=request_id).first()
        if not approval:
            return Response({"detail": "瀹℃壒鍗曚笉瀛樺湪"}, status=status.HTTP_404_NOT_FOUND)
        if approval.status != OperationApproval.STATUS_PENDING:
            return Response(
                {"detail": f"褰撳墠鐘舵€佷负 {approval.status}锛屼笉鑳芥墽琛屽鎵归€氳繃"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApprovalDecisionSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        note = serializer.validated_data.get("note", "")

        approval.status = OperationApproval.STATUS_APPROVED
        approval.approved_by = request.user
        approval.approved_at = timezone.now()
        if note:
            approval.reason = (approval.reason + f"\n[APPROVE_NOTE] {note}").strip()
        approval.save(update_fields=["status", "approved_by", "approved_at", "reason", "updated_at"])

        create_audit_log(
            approval=approval,
            event_type="approved",
            actor=request.user,
            client_ip=get_client_ip(request),
            result_snapshot={"status": approval.status},
            message=note or "瀹℃壒閫氳繃",
        )
        return Response(OperationApprovalSerializer(approval).data, status=status.HTTP_200_OK)


class ApprovalRejectAPIView(AdminOnlyAPIView):
    def post(self, request, request_id):
        approval = OperationApproval.objects.filter(request_id=request_id).first()
        if not approval:
            return Response({"detail": "瀹℃壒鍗曚笉瀛樺湪"}, status=status.HTTP_404_NOT_FOUND)
        if approval.status not in {OperationApproval.STATUS_PENDING, OperationApproval.STATUS_APPROVED}:
            return Response(
                {"detail": f"current status is {approval.status}; only pending/approved can be rejected"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ApprovalDecisionSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        note = serializer.validated_data.get("note", "")

        approval.status = OperationApproval.STATUS_REJECTED
        if note:
            approval.reason = (approval.reason + f"\n[REJECT_NOTE] {note}").strip()
        approval.save(update_fields=["status", "reason", "updated_at"])

        create_audit_log(
            approval=approval,
            event_type="rejected",
            actor=request.user,
            client_ip=get_client_ip(request),
            result_snapshot={"status": approval.status},
            message=note or "瀹℃壒椹冲洖",
        )
        return Response(OperationApprovalSerializer(approval).data, status=status.HTTP_200_OK)


class ApprovalExecuteAPIView(AdminOnlyAPIView):
    def post(self, request, request_id):
        approval = OperationApproval.objects.filter(request_id=request_id).first()
        if not approval:
            return Response({"detail": "瀹℃壒鍗曚笉瀛樺湪"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ApprovalExecuteSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        force = serializer.validated_data.get("force", False)

        if approval.status == OperationApproval.STATUS_EXECUTED and not force:
            output = OperationApprovalSerializer(approval).data
            output["_already_executed"] = True
            return Response(output, status=status.HTTP_200_OK)

        if approval.status != OperationApproval.STATUS_APPROVED and not force:
            return Response(
                {"detail": f"current status is {approval.status}; only approved can execute unless force=true"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = execute_approval(approval, actor=request.user)
            mark_approval_executed(approval, result=result, actor=request.user)
            create_audit_log(
                approval=approval,
                event_type="executed",
                actor=request.user,
                client_ip=get_client_ip(request),
                request_snapshot=approval.payload,
                result_snapshot=result,
                message="瀹℃壒鍔ㄤ綔鎵ц鎴愬姛",
            )
            return Response(OperationApprovalSerializer(approval).data, status=status.HTTP_200_OK)
        except Exception as exc:
            mark_approval_failed(approval, error_message=str(exc))
            create_audit_log(
                approval=approval,
                event_type="failed",
                actor=request.user,
                client_ip=get_client_ip(request),
                request_snapshot=approval.payload,
                result_snapshot={"error": str(exc)},
                message="瀹℃壒鍔ㄤ綔鎵ц澶辫触",
            )
            return Response(
                {
                    "detail": "鎵ц澶辫触",
                    "error": str(exc),
                    "approval": OperationApprovalSerializer(approval).data,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DashboardSummaryAPIView(AdminOnlyAPIView):
    def get(self, request):
        now = timezone.now()
        today = timezone.localdate(now) if timezone.is_aware(now) else now.date()
        week_days = [today - timedelta(days=offset) for offset in range(6, -1, -1)]

        base_qs = OperationApproval.objects.all()
        counts = {
            "pending": base_qs.filter(status=OperationApproval.STATUS_PENDING).count(),
            "approved": base_qs.filter(status=OperationApproval.STATUS_APPROVED).count(),
            "executed": base_qs.filter(status=OperationApproval.STATUS_EXECUTED).count(),
            "failed": base_qs.filter(status=OperationApproval.STATUS_FAILED).count(),
            "rejected": base_qs.filter(status=OperationApproval.STATUS_REJECTED).count(),
            "total": base_qs.count(),
        }

        in_24h_from = now - timedelta(hours=24)
        in_24h = {
            "requested": base_qs.filter(requested_at__gte=in_24h_from).count(),
            "executed": base_qs.filter(executed_at__gte=in_24h_from).count(),
            "failed": base_qs.filter(failed_at__gte=in_24h_from).count(),
        }

        rows = (
            base_qs.filter(requested_at__date__gte=week_days[0], requested_at__date__lte=week_days[-1])
            .annotate(day=TruncDate("requested_at"))
            .values("day", "status")
            .annotate(total=Count("id"))
            .order_by("day")
        )

        day_status_map = {}
        for row in rows:
            day = row.get("day")
            if not day:
                continue
            status_key = str(row.get("status") or "")
            day_status_map.setdefault(day, {})[status_key] = int(row.get("total") or 0)

        trend = []
        for day in week_days:
            status_counter = day_status_map.get(day, {})
            trend.append(
                {
                    "date": day.isoformat(),
                    "pending": status_counter.get(OperationApproval.STATUS_PENDING, 0),
                    "approved": status_counter.get(OperationApproval.STATUS_APPROVED, 0),
                    "executed": status_counter.get(OperationApproval.STATUS_EXECUTED, 0),
                    "failed": status_counter.get(OperationApproval.STATUS_FAILED, 0),
                    "rejected": status_counter.get(OperationApproval.STATUS_REJECTED, 0),
                    "total": sum(status_counter.values()),
                }
            )

        return Response(
            {
                "generated_at": now.isoformat(),
                "counts": counts,
                "in_24h": in_24h,
                "trend_7d": trend,
            },
            status=status.HTTP_200_OK,
        )


def _to_bool_query(value, default=True):
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "on"}:
        return True
    if text in {"0", "false", "no", "n", "off"}:
        return False
    return default


def _ops_probe_url(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=8) as resp:
            body = resp.read(4000).decode("utf-8", "ignore")
            return {
                "url": url,
                "status": int(getattr(resp, "status", 200) or 200),
                "body_has_challenge": "just a moment" in body.lower(),
                "error": "",
            }
    except HTTPError as exc:
        try:
            body = exc.read(4000).decode("utf-8", "ignore")
        except Exception:
            body = ""
        return {
            "url": url,
            "status": int(getattr(exc, "code", 0) or 0),
            "body_has_challenge": "just a moment" in body.lower(),
            "error": str(exc),
        }
    except URLError as exc:
        return {
            "url": url,
            "status": 0,
            "body_has_challenge": False,
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "url": url,
            "status": 0,
            "body_has_challenge": False,
            "error": str(exc),
        }


def _status_of_check(*, ok=False, warn=False, pending=False):
    if ok:
        return "ok"
    if warn:
        return "warn"
    if pending:
        return "pending"
    return "error"


class DailyAutomationHealthAPIView(AdminOnlyAPIView):
    def get(self, request):
        from game_article.models import Article
        from seo_automation.models import CrawlerTask, SeoArticle
        from .models import DailyRobotRun

        now = timezone.now()
        today = now.date()
        include_probe = _to_bool_query(request.query_params.get("include_probe"), default=True)

        config = DailyRobotConfig.get_solo()
        runs_today_qs = DailyRobotRun.objects.filter(run_date=today).order_by("-started_at", "-id")
        latest_run = runs_today_qs.first()

        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        today_tasks_qs = CrawlerTask.objects.filter(created_at__gte=today_start, created_at__lt=today_end)
        today_auto_tasks_qs = today_tasks_qs.filter(name__icontains="Auto Daily SEO")
        today_seo_qs = SeoArticle.objects.filter(created_at__gte=today_start, created_at__lt=today_end)
        today_article_qs = Article.objects.filter(created_at__gte=today_start, created_at__lt=today_end)

        stale_cutoff = now - timedelta(minutes=30)
        stale_inflight_qs = CrawlerTask.objects.filter(
            status__in=["pending", "crawling", "enriching", "seoing", "rewriting", "publishing"],
            updated_at__lt=stale_cutoff,
        )
        stale_inflight_sample = list(
            stale_inflight_qs.order_by("updated_at", "id").values("id", "name", "status", "progress", "updated_at")[:20]
        )

        seo_published_qs = SeoArticle.objects.filter(status="published")
        seo_published_total = seo_published_qs.count()
        seo_published_linked = seo_published_qs.filter(published_article__isnull=False).count()
        seo_published_unlinked = max(0, seo_published_total - seo_published_linked)

        recent_published_articles = list(Article.objects.filter(status="published").order_by("-published_at", "-id")[:60])
        recent_published_count = len(recent_published_articles)
        recent_missing_cover_count = sum(1 for item in recent_published_articles if not bool(item.cover_image))

        probe = {}
        if include_probe:
            probe = {
                "acg_search": _ops_probe_url("https://acg.gamer.com.tw/search.php?s=1&keyword=LINE%20Rangers"),
                "bahamut_board": _ops_probe_url("https://forum.gamer.com.tw/B.php?bsn=36730"),
            }

        latest_run_elapsed_minutes = 0
        if latest_run and latest_run.started_at:
            try:
                latest_run_elapsed_minutes = int(max(0, (now - latest_run.started_at).total_seconds()) // 60)
            except Exception:
                latest_run_elapsed_minutes = 0

        today_auto_failed = today_auto_tasks_qs.filter(status="failed").count()
        today_auto_completed = today_auto_tasks_qs.filter(status="completed").count()
        today_auto_total = today_auto_tasks_qs.count()

        check_rows = []
        check_rows.append(
            {
                "key": "daily_config_enabled",
                "name": "每日任务配置已启用",
                "status": _status_of_check(ok=bool(config.is_enabled)),
                "evidence": f"is_enabled={bool(config.is_enabled)}, daily_hour={int(config.daily_hour)}, poll_seconds={int(config.poll_seconds)}",
                "suggestion": "若关闭请在“每日任务配置”中启用并保存。",
            }
        )
        check_rows.append(
            {
                "key": "scheduler_trigger_today",
                "name": "今日定时器已触发",
                "status": _status_of_check(ok=runs_today_qs.exists()),
                "evidence": f"runs_today={runs_today_qs.count()}",
                "suggestion": "若未触发，先检查进程常驻状态和应用启动日志。",
            }
        )

        run_status_text = str(getattr(latest_run, "status", "") or "")
        run_warn = False
        run_pending = False
        if latest_run:
            if run_status_text == "running":
                run_pending = True
                if latest_run_elapsed_minutes >= int(config.max_running_minutes):
                    run_warn = True
                    run_pending = False
            elif run_status_text == "failed":
                run_warn = True
            elif run_status_text in {"completed", "partial"}:
                run_warn = False
            else:
                run_pending = True

        check_rows.append(
            {
                "key": "latest_run_health",
                "name": "最新日任务运行健康",
                "status": _status_of_check(
                    ok=bool(latest_run and run_status_text in {"completed", "partial"}),
                    warn=run_warn,
                    pending=bool(latest_run and run_pending),
                ),
                "evidence": (
                    f"latest_run_id={getattr(latest_run, 'id', None)}, "
                    f"status={run_status_text or '-'}, "
                    f"elapsed_min={latest_run_elapsed_minutes}, "
                    f"max_running_minutes={int(config.max_running_minutes)}"
                ),
                "suggestion": "持续 running 或 failed 需要查看 run 详情并定位卡点（常见为外部源阻断或 Step5 超时）。",
            }
        )

        auto_daily_pending = bool(latest_run and run_status_text == "running" and today_auto_total == 0)
        check_rows.append(
            {
                "key": "today_auto_daily_task_created",
                "name": "今日已创建 Auto Daily SEO 任务",
                "status": _status_of_check(
                    ok=today_auto_total > 0,
                    warn=bool(runs_today_qs.exists() and today_auto_total == 0 and not auto_daily_pending),
                    pending=auto_daily_pending,
                ),
                "evidence": f"today_auto_daily_tasks={today_auto_total}, today_tasks_total={today_tasks_qs.count()}",
                "suggestion": "若长期为 0，检查选题阶段（榜单/BSN）和外部抓取是否被拦截。",
            }
        )

        check_rows.append(
            {
                "key": "today_auto_daily_task_result",
                "name": "今日 Auto Daily SEO 任务结果",
                "status": _status_of_check(
                    ok=bool(today_auto_total > 0 and today_auto_failed == 0),
                    warn=bool(today_auto_total > 0 and today_auto_failed > 0),
                    pending=bool(today_auto_total == 0 and runs_today_qs.exists()),
                ),
                "evidence": f"completed={today_auto_completed}, failed={today_auto_failed}",
                "suggestion": "若失败，请优先看 failed 任务的 error_message 与 result_payload.summary。",
            }
        )

        check_rows.append(
            {
                "key": "stale_inflight_guard",
                "name": "卡住任务监控（30 分钟）",
                "status": _status_of_check(ok=stale_inflight_qs.count() == 0, warn=stale_inflight_qs.count() > 0),
                "evidence": f"stale_inflight_count={stale_inflight_qs.count()}",
                "suggestion": "若>0，需检查超时保护是否在入口被触发，并定位卡住阶段。",
            }
        )

        link_gap_ratio = (seo_published_unlinked / seo_published_total) if seo_published_total else 0.0
        check_rows.append(
            {
                "key": "publish_link_integrity",
                "name": "SEO 发布与资讯挂接一致性",
                "status": _status_of_check(
                    ok=seo_published_unlinked == 0,
                    warn=seo_published_unlinked > 0 and link_gap_ratio <= 0.2,
                ),
                "evidence": (
                    f"seo_published_total={seo_published_total}, "
                    f"linked={seo_published_linked}, unlinked={seo_published_unlinked}"
                ),
                "suggestion": "存在 unlinked 时，需排查发布流程中 published_article 关系写回与后续数据修复逻辑。",
            }
        )

        check_rows.append(
            {
                "key": "recent_cover_integrity",
                "name": "近期资讯封面完整性",
                "status": _status_of_check(
                    ok=recent_published_count == 0 or recent_missing_cover_count == 0,
                    warn=recent_published_count > 0 and recent_missing_cover_count > 0,
                ),
                "evidence": f"recent_published={recent_published_count}, missing_cover={recent_missing_cover_count}",
                "suggestion": "缺封面会影响资讯列表观感，建议补跑封面修复或校验图片源质量。",
            }
        )

        if include_probe:
            acg = probe.get("acg_search") or {}
            bsn = probe.get("bahamut_board") or {}
            probe_ok = (
                int(acg.get("status") or 0) == 200
                and int(bsn.get("status") or 0) == 200
                and not bool(acg.get("body_has_challenge"))
                and not bool(bsn.get("body_has_challenge"))
            )
            check_rows.append(
                {
                    "key": "upstream_connectivity",
                    "name": "外部源连通性（Bahamut）",
                    "status": _status_of_check(ok=probe_ok, warn=not probe_ok),
                    "evidence": (
                        f"acg_status={acg.get('status')}, acg_challenge={bool(acg.get('body_has_challenge'))}, "
                        f"bahamut_status={bsn.get('status')}, bahamut_challenge={bool(bsn.get('body_has_challenge'))}"
                    ),
                    "suggestion": "若出现 403/challenge，需更换抓取策略或代理链路，否则会直接影响每日任务产出。",
                }
            )

        recent_runs = list(
            DailyRobotRun.objects.filter(run_date__gte=today - timedelta(days=6))
            .order_by("-run_date", "-started_at", "-id")
            .values("id", "run_date", "status", "trigger_source", "started_at", "finished_at")[:20]
        )

        response_payload = {
            "generated_at": now.isoformat(),
            "today": str(today),
            "config": {
                "is_enabled": bool(config.is_enabled),
                "daily_hour": int(config.daily_hour),
                "poll_seconds": int(config.poll_seconds),
                "max_running_minutes": int(config.max_running_minutes),
                "publish_status": str(config.publish_status),
                "import_limit": int(config.import_limit),
                "limit_games": int(config.limit_games),
                "posts_min": int(config.posts_min),
                "posts_max": int(config.posts_max),
                "max_attempts_per_game": int(config.max_attempts_per_game),
                "rewrite_limit": int(config.rewrite_limit),
                "review_threshold": int(config.review_threshold),
                "recent_days": int(config.recent_days),
            },
            "runs_today": int(runs_today_qs.count()),
            "latest_run": {
                "id": getattr(latest_run, "id", None),
                "status": run_status_text,
                "trigger_source": str(getattr(latest_run, "trigger_source", "") or ""),
                "started_at": str(getattr(latest_run, "started_at", "") or ""),
                "finished_at": str(getattr(latest_run, "finished_at", "") or ""),
                "error_message": str(getattr(latest_run, "error_message", "") or "")[:300],
                "elapsed_minutes": latest_run_elapsed_minutes,
            },
            "recent_runs_7d": [
                {
                    "id": int(row["id"]),
                    "run_date": str(row["run_date"]),
                    "status": str(row["status"] or ""),
                    "trigger_source": str(row["trigger_source"] or ""),
                    "started_at": str(row["started_at"] or ""),
                    "finished_at": str(row["finished_at"] or ""),
                }
                for row in recent_runs
            ],
            "today_counts": {
                "task_total": int(today_tasks_qs.count()),
                "task_auto_daily": int(today_auto_total),
                "task_failed": int(today_tasks_qs.filter(status="failed").count()),
                "task_completed": int(today_tasks_qs.filter(status="completed").count()),
                "seo_article_created": int(today_seo_qs.count()),
                "seo_article_published": int(
                    SeoArticle.objects.filter(published_at__gte=today_start, published_at__lt=today_end).count()
                ),
                "article_created": int(today_article_qs.count()),
                "article_published": int(
                    Article.objects.filter(published_at__gte=today_start, published_at__lt=today_end).count()
                ),
            },
            "integrity": {
                "seo_published_total": int(seo_published_total),
                "seo_published_linked": int(seo_published_linked),
                "seo_published_unlinked": int(seo_published_unlinked),
                "recent_published_checked": int(recent_published_count),
                "recent_missing_cover_count": int(recent_missing_cover_count),
            },
            "stale_inflight": {
                "count": int(stale_inflight_qs.count()),
                "sample": [
                    {
                        "id": int(row["id"]),
                        "name": str(row.get("name") or "")[:160],
                        "status": str(row.get("status") or ""),
                        "progress": int(row.get("progress") or 0),
                        "updated_at": str(row.get("updated_at") or ""),
                    }
                    for row in stale_inflight_sample
                ],
            },
            "checklist": check_rows,
            "connectivity_probe": probe,
        }
        return Response(response_payload, status=status.HTTP_200_OK)


class SeoArticleOptionsAPIView(AdminOnlyAPIView):
    def get(self, request):
        from seo_automation.models import SeoArticle

        limit = request.query_params.get("limit")
        try:
            n = max(1, min(200, int(limit))) if limit else 50
        except Exception:
            n = 50

        rows = (
            SeoArticle.objects.select_related("game", "task", "published_article")
            .order_by("-id")
            .values(
                "id",
                "title",
                "status",
                "source_url",
                "created_at",
                "game__title",
                "task__keyword",
                "published_article_id",
            )[:n]
        )

        results = []
        for row in rows:
            results.append(
                {
                    "id": row["id"],
                    "title": row.get("title") or "",
                    "status": row.get("status") or "",
                    "source_url": row.get("source_url") or "",
                    "created_at": row.get("created_at").isoformat() if row.get("created_at") else "",
                    "game_title": row.get("game__title") or "",
                    "task_keyword": row.get("task__keyword") or "",
                    "published_article_id": row.get("published_article_id"),
                }
            )

        return Response(
            {
                "count": len(results),
                "results": results,
            },
            status=status.HTTP_200_OK,
        )


class DailyRobotConfigAPIView(AdminOnlyAPIView):
    def get(self, request):
        config_obj = DailyRobotConfig.get_solo()
        data = DailyRobotConfigSerializer(config_obj).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        config_obj = DailyRobotConfig.get_solo()
        serializer = DailyRobotConfigSerializer(
            config_obj,
            data=request.data or {},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        saved = serializer.save(updated_by=request.user)
        return Response(DailyRobotConfigSerializer(saved).data, status=status.HTTP_200_OK)


class AutomationGooglePlayImportAPIView(AdminOnlyAPIView):
    def post(self, request):
        serializer = AutomationGooglePlayImportSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            result = run_google_play_import_automation(
                actor=request.user,
                play_urls=data.get("play_urls") or [],
                package_ids=data.get("package_ids") or [],
                template_key=str(data.get("template_key") or "default"),
                category_id=data.get("category_id"),
                publish_status=str(data.get("publish_status") or "draft"),
                overwrite_existing=bool(data.get("overwrite_existing", False)),
                limit=int(data.get("limit") or 20),
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {"detail": "automation_google_play_import_failed", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AutomationSeoDailyRunAPIView(AdminOnlyAPIView):
    def post(self, request):
        serializer = AutomationSeoDailyRunSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            result = run_seo_daily_automation(
                actor=request.user,
                game_ids=data.get("game_ids") or [],
                limit_games=int(data.get("limit_games") or 6),
                posts_min=int(data.get("posts_min") or 10),
                posts_max=int(data.get("posts_max") or 20),
                max_attempts_per_game=int(data.get("max_attempts_per_game") or 1),
                rewrite_limit=int(data.get("rewrite_limit") or 1),
                publish_status=str(data.get("publish_status") or "published"),
                publish_now=bool(data.get("publish_now", True)),
                rewrite_low_quality=bool(data.get("rewrite_low_quality", True)),
                review_threshold=int(data.get("review_threshold") or 72),
                recent_days=int(data.get("recent_days") or 30),
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {"detail": "automation_seo_daily_run_failed", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AutomationPublishedReviewAPIView(AdminOnlyAPIView):
    def post(self, request):
        serializer = AutomationPublishedReviewSerializer(data=request.data or {})
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            result = run_published_article_recheck_automation(
                actor=request.user,
                game_ids=data.get("game_ids") or [],
                limit=int(data.get("limit") or 100),
                rewrite_low_quality=bool(data.get("rewrite_low_quality", True)),
                archive_duplicates=bool(data.get("archive_duplicates", True)),
                review_threshold=int(data.get("review_threshold") or 72),
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {"detail": "automation_review_published_failed", "error": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ApprovalLogsAPIView(AdminOnlyAPIView):
    def get(self, request, request_id):
        approval = OperationApproval.objects.filter(request_id=request_id).first()
        if not approval:
            return Response({"detail": "approval request not found"}, status=status.HTTP_404_NOT_FOUND)

        limit = request.query_params.get("limit")
        try:
            n = max(1, min(200, int(limit))) if limit else 100
        except Exception:
            n = 100

        logs_qs = approval.audit_logs.all().order_by("-created_at", "-id")[:n]
        data = OperationAuditLogSerializer(logs_qs, many=True).data
        return Response(
            {
                "request_id": str(approval.request_id),
                "count": len(data),
                "results": data,
            },
            status=status.HTTP_200_OK,
        )
