from django.contrib import admin
from .models import GameCategory, Game, ProductType, Product


@admin.register(GameCategory)
class GameCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'sort_order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    list_editable = ['sort_order', 'is_active']
    ordering = ['sort_order']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'developer', 'is_hot', 'is_active', 'view_count', 'sort_order', 'created_at']
    list_filter = ['category', 'is_hot', 'is_active', 'created_at']
    search_fields = ['name', 'developer']
    list_editable = ['is_hot', 'is_active', 'sort_order']
    readonly_fields = ['view_count', 'created_at', 'updated_at']
    
    class Media:
        js = ('admin/js/media_picker_widget.js',)
        css = {
            'all': ('admin/css/media_picker.css',)
        }

    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'category', 'developer', 'description')
        }),
        ('图片', {
            'fields': ('icon', 'cover')
        }),
        ('设置', {
            'fields': ('is_hot', 'is_active', 'sort_order')
        }),
        ('统计信息', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'game', 'product_type', 'current_price', 'discount', 'stock', 'sales_count', 'is_hot', 'is_recommended', 'is_active', 'created_at']
    list_filter = ['game', 'product_type', 'is_hot', 'is_recommended', 'is_active', 'created_at']
    search_fields = ['name', 'game__name']
    list_editable = ['is_hot', 'is_recommended', 'is_active']
    readonly_fields = ['discount', 'sales_count', 'created_at', 'updated_at']
    
    class Media:
        js = ('admin/js/media_picker_widget.js',)
        css = {
            'all': ('admin/css/media_picker.css',)
        }

    fieldsets = (
        ('基本信息', {
            'fields': ('game', 'product_type', 'name', 'description')
        }),
        ('价格信息', {
            'fields': ('original_price', 'current_price', 'discount')
        }),
        ('库存与销量', {
            'fields': ('stock', 'sales_count')
        }),
        ('图片', {
            'fields': ('product_image',)
        }),
        ('设置', {
            'fields': ('is_hot', 'is_recommended', 'is_active', 'sort_order')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
