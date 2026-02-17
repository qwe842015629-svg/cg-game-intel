from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 用户扩展信息模型
class UserProfile(models.Model):
    """用户扩展信息"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='用户')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='账户余额')
    points = models.IntegerField(default=0, verbose_name='积分')
    vip_level = models.IntegerField(default=0, verbose_name='VIP等级')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'user_profile'
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}的资料"


# 信号：创建用户时自动创建用户资料
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """当创建新用户时，自动创建用户资料"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """保存用户时，同时保存用户资料"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
