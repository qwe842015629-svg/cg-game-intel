from django.contrib import admin
from .models import ContactMethod, FAQ, CustomerServiceConfig


@admin.register(ContactMethod)
class ContactMethodAdmin(admin.ModelAdmin):
    """联系方式管理"""
    list_display = ['contact_type', 'title', 'contact_info', 'is_active', 'sort_order', 'updated_at']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['contact_type', 'is_active']
    search_fields = ['title', 'description', 'contact_info']
    ordering = ['sort_order', 'id']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('contact_type', 'title', 'description', 'contact_info')
        }),
        ('显示设置', {
            'fields': ('icon', 'button_text', 'button_link')
        }),
        ('状态', {
            'fields': ('is_active', 'sort_order')
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    """常见问题管理"""
    list_display = ['question', 'category', 'is_active', 'sort_order', 'view_count', 'updated_at']
    list_editable = ['is_active', 'sort_order']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'answer']
    ordering = ['sort_order', '-created_at']
    
    fieldsets = (
        ('问题内容', {
            'fields': ('question', 'answer', 'category')
        }),
        ('状态', {
            'fields': ('is_active', 'sort_order', 'view_count')
        }),
    )
    
    readonly_fields = ['view_count']


@admin.register(CustomerServiceConfig)
class CustomerServiceConfigAdmin(admin.ModelAdmin):
    """客服页面配置管理"""
    list_display = ['page_title', 'show_contact_methods', 'show_faq', 'updated_at']
    
    fieldsets = (
        ('页面设置', {
            'fields': ('page_title', 'page_description')
        }),
        ('显示选项', {
            'fields': ('show_contact_methods', 'show_faq', 'faq_title')
        }),
    )
    
    def has_add_permission(self, request):
        # 只允许有一条配置记录
        return not CustomerServiceConfig.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # 不允许删除配置
        return False
