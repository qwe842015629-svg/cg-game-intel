from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

# 用户资料内联编辑
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = '用户资料'
    verbose_name_plural = '用户资料'
    fields = (
        'display_name',
        ('gender', 'phone'),
        'bio',
        'avatar',
        ('sandbox_enabled', 'ai_content_visibility', 'ai_isolation_mode'),
        'sandbox_namespace',
        ('balance', 'points', 'vip_level'),
    )
    readonly_fields = ('sandbox_namespace',)

# 扩展用户管理
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'get_balance', 'get_points')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    def get_balance(self, obj):
        """获取用户余额"""
        if hasattr(obj, 'profile'):
            return f'￥{obj.profile.balance}'
        return '￥0.00'
    get_balance.short_description = '账户余额'
    
    def get_points(self, obj):
        """获取用户积分"""
        if hasattr(obj, 'profile'):
            return obj.profile.points
        return 0
    get_points.short_description = '积分'

# 重新注册User模型
unregister = getattr(admin.site, 'unregister', None)
if unregister:
    try:
        admin.site.unregister(User)
    except admin.sites.NotRegistered:
        pass

admin.site.register(User, UserAdmin)
