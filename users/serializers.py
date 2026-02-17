from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """用户资料序列化器"""
    
    class Meta:
        model = UserProfile
        fields = ['phone', 'avatar', 'balance', 'points', 'vip_level', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined', 'is_active']


class UserListSerializer(serializers.ModelSerializer):
    """用户列表序列化器（简化版）"""
    balance = serializers.SerializerMethodField()
    points = serializers.SerializerMethodField()
    vip_level = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'is_active', 'date_joined', 'balance', 'points', 'vip_level']
    
    def get_balance(self, obj):
        """获取余额"""
        if hasattr(obj, 'profile'):
            return str(obj.profile.balance)
        return "0.00"
    
    def get_points(self, obj):
        """获取积分"""
        if hasattr(obj, 'profile'):
            return obj.profile.points
        return 0
    
    def get_vip_level(self, obj):
        """获取VIP等级"""
        if hasattr(obj, 'profile'):
            return obj.profile.vip_level
        return 0
