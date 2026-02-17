import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from game_article.models import Article
from game_page.models import GamePage


class LLMApiSetting(models.Model):
    """Runtime LLM API configuration used by SEO rewrite pipeline."""

    name = models.CharField(max_length=80, unique=True, default="default")
    base_url = models.CharField(max_length=255, blank=True, default="")
    api_key = models.CharField(max_length=255, blank=True, default="")
    model_name = models.CharField(max_length=120, default="grok-4-fast")
    timeout_seconds = models.PositiveIntegerField(default=45)
    is_active = models.BooleanField(default=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_llm_api_settings",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "id"]

    def __str__(self):
        return f"{self.name} ({self.model_name})"

    @classmethod
    def get_solo(cls):
        setting = cls.objects.filter(is_active=True).order_by("-updated_at", "-id").first()
        if setting:
            updates = []
            if not setting.base_url:
                setting.base_url = "https://api.x.ai/v1"
                updates.append("base_url")
            if not setting.model_name:
                setting.model_name = "grok-4-fast"
                updates.append("model_name")
            if updates:
                updates.append("updated_at")
                setting.save(update_fields=updates)
            return setting
        setting, _ = cls.objects.get_or_create(
            name="default",
            defaults={
                "base_url": "https://api.x.ai/v1",
                "model_name": "grok-4-fast",
                "timeout_seconds": 45,
                "is_active": True,
            },
        )
        if not setting.is_active:
            setting.is_active = True
            setting.save(update_fields=["is_active", "updated_at"])
        if not setting.base_url:
            setting.base_url = "https://api.x.ai/v1"
            setting.save(update_fields=["base_url", "updated_at"])
        if not setting.model_name:
            setting.model_name = "grok-4-fast"
            setting.save(update_fields=["model_name", "updated_at"])
        return setting


class CrawlerTask(models.Model):
    """Crawler task state for the SEO automation pipeline."""

    SOURCE_CHOICES = [
        ("bahamut", "Bahamut"),
        ("forum", "Forum"),
        ("manual", "Manual"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("crawling", "Crawling"),
        ("rewriting", "Rewriting"),
        ("enriching", "Enriching"),
        ("seoing", "Seoing"),
        ("publishing", "Publishing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    name = models.CharField(max_length=200, blank=True, default="")
    source_platform = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default="bahamut",
    )
    source_url = models.URLField(blank=True, default="")
    keyword = models.CharField(max_length=120)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    progress = models.PositiveSmallIntegerField(default=0)
    result_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    request_payload = models.JSONField(default=dict, blank=True)
    result_payload = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    triggered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_crawler_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["keyword"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        name = self.name or self.keyword
        return f"{name} ({self.status})"


class SeoKeywordWeight(models.Model):
    """Weighted keywords used for SEO prompt composition."""

    keyword = models.CharField(max_length=120)
    keyword_group = models.CharField(max_length=100, blank=True, default="general")
    intent = models.CharField(max_length=50, blank=True, default="informational")
    weight = models.DecimalField(max_digits=6, decimal_places=3, default=1.000)
    language = models.CharField(max_length=20, default="zh-TW")
    locale = models.CharField(max_length=20, default="zh-TW")
    synonyms = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-weight", "keyword"]
        unique_together = [("keyword", "language", "locale")]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["keyword_group"]),
            models.Index(fields=["weight"]),
        ]

    def __str__(self):
        return f"{self.keyword} ({self.weight})"


class SeoArticle(models.Model):
    """Structured SEO article draft generated by the pipeline."""

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("review", "Review"),
        ("published", "Published"),
        ("failed", "Failed"),
    ]

    SOURCE_CHOICES = [
        ("bahamut", "Bahamut"),
        ("forum", "Forum"),
        ("manual", "Manual"),
    ]

    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True, null=True)
    game = models.ForeignKey(
        GamePage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_articles",
    )
    task = models.ForeignKey(
        CrawlerTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_articles",
    )
    published_article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_source_articles",
    )
    source_platform = models.CharField(
        max_length=30,
        choices=SOURCE_CHOICES,
        default="bahamut",
    )
    source_title = models.CharField(max_length=255, blank=True, default="")
    source_url = models.URLField(blank=True, default="")
    source_published_at = models.DateTimeField(null=True, blank=True)
    raw_text = models.TextField(blank=True, default="")
    body_html = models.TextField()
    tags = models.JSONField(default=list, blank=True)
    meta_title = models.CharField(max_length=120, blank=True, default="")
    meta_description = models.CharField(max_length=220, blank=True, default="")
    seo_score = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    publish_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    rewrite_model = models.CharField(max_length=80, blank=True, default="")
    rewrite_payload = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seo_articles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["game"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "seo-article"
            candidate = base_slug
            while SeoArticle.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
                candidate = f"{base_slug}-{uuid.uuid4().hex[:6]}"
            self.slug = candidate

        if not self.meta_title:
            self.meta_title = (self.title or "")[:60]

        if self.meta_description:
            self.meta_description = self.meta_description[:160]

        super().save(*args, **kwargs)
