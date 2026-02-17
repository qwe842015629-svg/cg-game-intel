from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ContactMethodViewSet, FAQViewSet, CustomerServiceConfigViewSet

router = DefaultRouter()
router.register(r'contact-methods', ContactMethodViewSet, basename='contact-method')
router.register(r'faqs', FAQViewSet, basename='faq')
router.register(r'config', CustomerServiceConfigViewSet, basename='customer-service-config')

urlpatterns = [
    path('', include(router.urls)),
]
