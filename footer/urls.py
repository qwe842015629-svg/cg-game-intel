from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FooterSectionViewSet, FooterLinkViewSet, FooterConfigViewSet

router = DefaultRouter()
router.register(r'sections', FooterSectionViewSet, basename='footer-section')
router.register(r'links', FooterLinkViewSet, basename='footer-link')
router.register(r'config', FooterConfigViewSet, basename='footer-config')

urlpatterns = [
    path('', include(router.urls)),
]
