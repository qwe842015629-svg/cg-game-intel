from django.contrib import admin

from .models import CrawlerTask, LLMApiSetting, SeoArticle, SeoKeywordWeight


@admin.register(CrawlerTask)
class CrawlerTaskAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "keyword",
        "source_platform",
        "status",
        "progress",
        "result_count",
        "created_at",
    ]
    list_filter = ["source_platform", "status", "created_at"]
    search_fields = ["name", "keyword", "source_url", "error_message"]
    readonly_fields = ["created_at", "updated_at", "started_at", "finished_at"]
    ordering = ["-created_at"]


@admin.register(SeoKeywordWeight)
class SeoKeywordWeightAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "keyword",
        "keyword_group",
        "intent",
        "weight",
        "language",
        "locale",
        "is_active",
        "updated_at",
    ]
    list_filter = ["is_active", "language", "locale", "keyword_group", "intent"]
    search_fields = ["keyword", "notes"]
    list_editable = ["weight", "is_active"]
    ordering = ["-weight", "keyword"]


@admin.register(SeoArticle)
class SeoArticleAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "game",
        "status",
        "source_platform",
        "seo_score",
        "published_at",
        "created_at",
    ]
    list_filter = ["status", "source_platform", "created_at", "published_at"]
    search_fields = ["title", "source_title", "meta_description", "source_url"]
    readonly_fields = ["slug", "created_at", "updated_at", "published_at"]
    raw_id_fields = ["game", "task", "published_article", "created_by"]
    ordering = ["-created_at"]


@admin.register(LLMApiSetting)
class LLMApiSettingAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "name",
        "model_name",
        "base_url",
        "timeout_seconds",
        "is_active",
        "updated_at",
    ]
    list_filter = ["is_active", "updated_at"]
    search_fields = ["name", "model_name", "base_url"]
    list_editable = ["is_active", "timeout_seconds"]
    raw_id_fields = ["updated_by"]
    readonly_fields = ["created_at", "updated_at"]
    ordering = ["-updated_at"]
