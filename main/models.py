from django.conf import settings
from django.db import models


class HomeLayout(models.Model):
    """Homepage section layout configuration."""

    SECTION_CHOICES = [
        ("banner_section", "Homepage - Banner"),
        ("features", "Homepage - Features"),
        ("hot_games", "Homepage - Hot Games"),
        ("categories", "Homepage - Categories"),
        ("latest_news", "Homepage - Latest News"),
        ("articles_page", "Articles Page Header"),
        ("games_page", "Games Page Header"),
        ("customer_service", "Customer Service Header"),
        ("about_page", "About Page Header"),
        ("game_detail", "Game Detail Header"),
        ("login_page", "Login Page Header"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    section_key = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True, verbose_name="Section Key")
    section_name = models.CharField(max_length=100, verbose_name="Section Name")
    section_name_i18n = models.JSONField(default=dict, blank=True, verbose_name="Section Name I18n")
    is_enabled = models.BooleanField(default=True, verbose_name="Enabled")
    sort_order = models.IntegerField(default=0, verbose_name="Sort Order")
    config = models.JSONField(default=dict, blank=True, verbose_name="Section Config")
    config_i18n = models.JSONField(default=dict, blank=True, verbose_name="Section Config I18n")
    view_count = models.IntegerField(default=0, verbose_name="View Count")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Home Layout"
        verbose_name_plural = "Home Layout"
        ordering = ["sort_order", "created_at"]
        db_table = "layout"

    def __str__(self):
        return f"{self.section_name} ({'Enabled' if self.is_enabled else 'Disabled'})"

    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=["view_count"])


class SiteConfig(models.Model):
    """Global site configuration."""

    site_name = models.CharField(max_length=100, default="CYPHER GAME BUY", verbose_name="Site Name")
    site_logo = models.ImageField(upload_to="site/", blank=True, null=True, verbose_name="Site Logo")
    favicon = models.ImageField(upload_to="site/", blank=True, null=True, verbose_name="Favicon")
    seo_keywords = models.CharField(max_length=255, blank=True, verbose_name="SEO Keywords")
    seo_description = models.TextField(blank=True, verbose_name="SEO Description")
    primary_color = models.CharField(max_length=20, default="#1890ff", verbose_name="Primary Color")
    secondary_color = models.CharField(max_length=20, default="#52c41a", verbose_name="Secondary Color")
    contact_email = models.EmailField(blank=True, verbose_name="Contact Email")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Contact Phone")
    is_maintenance_mode = models.BooleanField(default=False, verbose_name="Maintenance Mode")
    theme_config = models.JSONField(default=dict, blank=True, verbose_name="Theme Config")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Site Config"
        verbose_name_plural = "Site Config"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        if not self.pk and SiteConfig.objects.exists():
            return SiteConfig.objects.first()
        return super().save(*args, **kwargs)


class Banner(models.Model):
    """Homepage banner."""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    title = models.CharField(max_length=200, verbose_name="Banner Title")
    title_i18n = models.JSONField(default=dict, blank=True, verbose_name="Banner Title I18n")
    description = models.TextField(max_length=500, blank=True, verbose_name="Banner Description")
    description_i18n = models.JSONField(default=dict, blank=True, verbose_name="Banner Description I18n")
    badge = models.CharField(max_length=50, blank=True, verbose_name="Badge Text")
    badge_i18n = models.JSONField(default=dict, blank=True, verbose_name="Badge Text I18n")
    image = models.ImageField(upload_to="banners/", verbose_name="Banner Image")
    primary_button_text = models.CharField(max_length=50, default="Recharge Now", verbose_name="Primary Button Text")
    primary_button_text_i18n = models.JSONField(default=dict, blank=True, verbose_name="Primary Button Text I18n")
    primary_button_link = models.CharField(max_length=500, default="/recharge", verbose_name="Primary Button Link")
    secondary_button_text = models.CharField(max_length=50, default="View Details", verbose_name="Secondary Button Text")
    secondary_button_text_i18n = models.JSONField(default=dict, blank=True, verbose_name="Secondary Button Text I18n")
    secondary_button_link = models.CharField(max_length=500, default="/games", verbose_name="Secondary Button Link")
    sort_order = models.IntegerField(default=0, verbose_name="Sort Order")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="Status")
    is_default = models.BooleanField(default=False, verbose_name="Default Banner")
    view_count = models.IntegerField(default=0, verbose_name="View Count")
    click_count = models.IntegerField(default=0, verbose_name="Click Count")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Banner"
        verbose_name_plural = "Banner"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title

    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=["view_count"])

    def increase_click_count(self):
        self.click_count += 1
        self.save(update_fields=["click_count"])


class MediaAsset(models.Model):
    """Central media library asset."""

    CATEGORY_CHOICES = [
        ("background", "Background"),
        ("icon", "Icon"),
        ("banner", "Banner"),
        ("ads", "Ads"),
        ("product", "Product"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=255, verbose_name="File Name")
    file = models.ImageField(upload_to="uploads/%Y/%m/", verbose_name="Asset File")
    thumbnail = models.ImageField(
        upload_to="uploads/thumbnails/%Y/%m/",
        blank=True,
        null=True,
        verbose_name="Thumbnail",
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other", verbose_name="Category")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Alt Text")
    file_size = models.IntegerField(default=0, verbose_name="File Size KB")
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        unique=True,
        db_index=True,
        verbose_name="Content Hash",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Media Asset"
        verbose_name_plural = "Media Asset"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def url(self):
        return self.file.url if self.file else ""

    @property
    def thumbnail_url(self):
        return self.thumbnail.url if self.thumbnail else (self.file.url if self.file else "")


class NovelDraft(models.Model):
    """Persisted novel writing draft scoped to user or anonymous client id."""

    owner_key = models.CharField(max_length=160, unique=True, db_index=True, verbose_name="Owner Key")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="novel_drafts",
        verbose_name="User",
    )
    client_id = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="Client ID")
    title = models.CharField(max_length=200, blank=True, default="", verbose_name="Draft Title")
    state = models.JSONField(default=dict, blank=True, verbose_name="Draft State")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Novel Draft"
        verbose_name_plural = "Novel Drafts"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or self.owner_key


class NovelWork(models.Model):
    """Persisted novel work scoped to user or anonymous client id."""

    class Visibility(models.IntegerChoices):
        PRIVATE = 0, "Private"
        FOLLOWERS = 1, "Followers"
        PUBLIC = 2, "Public"

    owner_key = models.CharField(max_length=160, db_index=True, verbose_name="Owner Key")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="novel_works",
        verbose_name="User",
    )
    client_id = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="Client ID")
    title = models.CharField(max_length=200, blank=True, default="", verbose_name="Title")
    summary = models.TextField(blank=True, default="", verbose_name="Summary")
    plan = models.JSONField(default=dict, blank=True, verbose_name="Plan")
    chapters = models.JSONField(default=list, blank=True, verbose_name="Chapters")
    cover_image = models.TextField(blank=True, default="", verbose_name="Cover Image")
    character_images = models.JSONField(default=list, blank=True, verbose_name="Character Images")
    chapter_images = models.JSONField(default=list, blank=True, verbose_name="Chapter Images")
    extra_meta = models.JSONField(default=dict, blank=True, verbose_name="Extra Meta")
    visibility = models.PositiveSmallIntegerField(
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
        verbose_name="Visibility",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Novel Work"
        verbose_name_plural = "Novel Works"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["owner_key", "-updated_at"]),
        ]

    def __str__(self):
        return self.title or f"work:{self.pk}"


class PlazaPost(models.Model):
    """Public square post shared by logged-in users or anonymous clients."""

    class Visibility(models.IntegerChoices):
        PRIVATE = 0, "Private"
        FOLLOWERS = 1, "Followers"
        PUBLIC = 2, "Public"

    POST_TYPE_CHOICES = [
        ("text", "Text"),
        ("role_card", "Role Card"),
        ("novel_work", "Novel Work"),
    ]

    owner_key = models.CharField(max_length=160, db_index=True, verbose_name="Owner Key")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="plaza_posts",
        verbose_name="User",
    )
    client_id = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="Client ID")
    author_name = models.CharField(max_length=80, blank=True, default="", verbose_name="Author Name")
    author_avatar = models.TextField(blank=True, default="", verbose_name="Author Avatar")
    content = models.TextField(blank=True, default="", verbose_name="Content")
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, default="text", verbose_name="Post Type")
    source_ref = models.CharField(max_length=128, blank=True, default="", verbose_name="Source Ref")
    source_data = models.JSONField(default=dict, blank=True, verbose_name="Source Data")
    visibility = models.PositiveSmallIntegerField(
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
        verbose_name="Visibility",
    )
    like_count = models.IntegerField(default=0, verbose_name="Like Count")
    comment_count = models.IntegerField(default=0, verbose_name="Comment Count")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Plaza Post"
        verbose_name_plural = "Plaza Posts"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["post_type", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.author_name or 'Anonymous'}:{self.post_type}:{self.pk}"


class PlazaLike(models.Model):
    """Like record for a plaza post."""

    post = models.ForeignKey(PlazaPost, on_delete=models.CASCADE, related_name="likes", verbose_name="Post")
    owner_key = models.CharField(max_length=160, db_index=True, verbose_name="Owner Key")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="plaza_likes",
        verbose_name="User",
    )
    client_id = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="Client ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")

    class Meta:
        verbose_name = "Plaza Like"
        verbose_name_plural = "Plaza Likes"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["post", "owner_key"], name="unique_plaza_post_like_owner"),
        ]

    def __str__(self):
        return f"like:{self.post_id}:{self.owner_key}"


class PlazaComment(models.Model):
    """Comment under a plaza post."""

    post = models.ForeignKey(PlazaPost, on_delete=models.CASCADE, related_name="comments", verbose_name="Post")
    owner_key = models.CharField(max_length=160, db_index=True, verbose_name="Owner Key")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="plaza_comments",
        verbose_name="User",
    )
    client_id = models.CharField(max_length=64, blank=True, default="", db_index=True, verbose_name="Client ID")
    author_name = models.CharField(max_length=80, blank=True, default="", verbose_name="Author Name")
    author_avatar = models.TextField(blank=True, default="", verbose_name="Author Avatar")
    content = models.TextField(verbose_name="Content")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")

    class Meta:
        verbose_name = "Plaza Comment"
        verbose_name_plural = "Plaza Comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
        ]

    def __str__(self):
        return f"comment:{self.post_id}:{self.pk}"
