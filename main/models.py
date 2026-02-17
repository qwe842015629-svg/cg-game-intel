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
    is_enabled = models.BooleanField(default=True, verbose_name="Enabled")
    sort_order = models.IntegerField(default=0, verbose_name="Sort Order")
    config = models.JSONField(default=dict, blank=True, verbose_name="Section Config")
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
    description = models.TextField(max_length=500, blank=True, verbose_name="Banner Description")
    badge = models.CharField(max_length=50, blank=True, verbose_name="Badge Text")
    image = models.ImageField(upload_to="banners/", verbose_name="Banner Image")
    primary_button_text = models.CharField(max_length=50, default="Recharge Now", verbose_name="Primary Button Text")
    primary_button_link = models.CharField(max_length=500, default="/recharge", verbose_name="Primary Button Link")
    secondary_button_text = models.CharField(max_length=50, default="View Details", verbose_name="Secondary Button Text")
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
