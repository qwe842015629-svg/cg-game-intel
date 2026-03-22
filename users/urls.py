from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CurrentUserDashboardView,
    UserDirectMessageInitView,
    UserDirectMessageReadView,
    UserDirectMessageThreadsView,
    UserDirectMessageMessagesView,
    UserFollowView,
    UserRelationListView,
    UserPublicRoleCardDetailView,
    UserPublicNovelWorkDetailView,
    CurrentUserProfileView,
    UserPublicProfileView,
    UserProfileViewSet,
    UserViewSet,
)

# 创建路由器
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='userprofile')

urlpatterns = [
    path('users/me/profile/', CurrentUserProfileView.as_view(), name='user-me-profile'),
    path('users/me/dashboard/', CurrentUserDashboardView.as_view(), name='user-me-dashboard'),
    path('users/<int:user_id>/profile/', UserPublicProfileView.as_view(), name='user-public-profile'),
    path('users/<int:user_id>/novels/<int:novel_id>/', UserPublicNovelWorkDetailView.as_view(), name='user-public-novel-detail'),
    path('users/<int:user_id>/characters/<int:character_id>/', UserPublicRoleCardDetailView.as_view(), name='user-public-character-detail'),
    path('users/<int:user_id>/follow/', UserFollowView.as_view(), name='user-follow'),
    path('users/<int:user_id>/followers/', UserRelationListView.as_view(), {'relation_mode': 'followers'}, name='user-followers'),
    path('users/<int:user_id>/following/', UserRelationListView.as_view(), {'relation_mode': 'following'}, name='user-following'),
    path('users/<int:user_id>/dm/init/', UserDirectMessageInitView.as_view(), name='user-dm-init'),
    path('users/dm/threads/', UserDirectMessageThreadsView.as_view(), name='user-dm-threads'),
    path('users/dm/threads/<int:thread_id>/messages/', UserDirectMessageMessagesView.as_view(), name='user-dm-thread-messages'),
    path('users/dm/threads/<int:thread_id>/read/', UserDirectMessageReadView.as_view(), name='user-dm-thread-read'),
    path('', include(router.urls)),
]
