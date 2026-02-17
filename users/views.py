from django.shortcuts import render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile
from .serializers import UserSerializer, UserListSerializer, UserProfileSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    用户API视图集
    
    list: 获取用户列表
    retrieve: 获取用户详情
    me: 获取当前登录用户信息
    """
    queryset = User.objects.filter(is_active=True).select_related('profile')
    permission_classes = [permissions.AllowAny]  # 允许所有人访问（可根据需求修改）
    
    def get_serializer_class(self):
        """根据操作返回不同的序列化器"""
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """获取当前登录用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取用户统计信息"""
        total_users = User.objects.filter(is_active=True).count()
        active_today = User.objects.filter(
            is_active=True,
            last_login__date=None  # 这里可以添加更复杂的逻辑
        ).count()
        
        return Response({
            'total_users': total_users,
            'active_users': total_users,  # 简化处理
            'new_users_today': 0,  # 可以添加实际逻辑
        })


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    用户资料API视图集
    
    list: 获取用户资料列表
    retrieve: 获取用户资料详情
    update: 更新用户资料
    """
    queryset = UserProfile.objects.all().select_related('user')
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """过滤查询集"""
        queryset = super().get_queryset()
        # 普通用户只能看到自己的资料
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        return queryset
