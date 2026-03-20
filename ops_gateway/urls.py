from django.urls import path

from .feishu_views import FeishuEventWebhookAPIView
from .views import (
    ApprovalApproveAPIView,
    ApprovalDetailAPIView,
    ApprovalExecuteAPIView,
    ApprovalListAPIView,
    ApprovalLogsAPIView,
    ApprovalRejectAPIView,
    DailyAutomationHealthAPIView,
    AutomationGooglePlayImportAPIView,
    AutomationPublishedReviewAPIView,
    AutomationSeoDailyRunAPIView,
    CreatePublishRequestAPIView,
    DailyRobotConfigAPIView,
    DashboardSummaryAPIView,
    SeoArticleOptionsAPIView,
)


urlpatterns = [
    path("feishu/events/", FeishuEventWebhookAPIView.as_view(), name="ops-feishu-events"),
    path("publish-requests/", CreatePublishRequestAPIView.as_view(), name="ops-publish-request-create"),
    path("automation/google-play-import/", AutomationGooglePlayImportAPIView.as_view(), name="ops-automation-google-play-import"),
    path("automation/seo-daily-run/", AutomationSeoDailyRunAPIView.as_view(), name="ops-automation-seo-daily-run"),
    path("automation/review-published/", AutomationPublishedReviewAPIView.as_view(), name="ops-automation-review-published"),
    path("automation/daily-config/", DailyRobotConfigAPIView.as_view(), name="ops-automation-daily-config"),
    path("automation/health-daily/", DailyAutomationHealthAPIView.as_view(), name="ops-automation-health-daily"),
    path("approvals/", ApprovalListAPIView.as_view(), name="ops-approval-list"),
    path("dashboard/summary/", DashboardSummaryAPIView.as_view(), name="ops-dashboard-summary"),
    path("seo-article-options/", SeoArticleOptionsAPIView.as_view(), name="ops-seo-article-options"),
    path("approvals/<uuid:request_id>/", ApprovalDetailAPIView.as_view(), name="ops-approval-detail"),
    path("approvals/<uuid:request_id>/logs/", ApprovalLogsAPIView.as_view(), name="ops-approval-logs"),
    path("approvals/<uuid:request_id>/approve/", ApprovalApproveAPIView.as_view(), name="ops-approval-approve"),
    path("approvals/<uuid:request_id>/reject/", ApprovalRejectAPIView.as_view(), name="ops-approval-reject"),
    path("approvals/<uuid:request_id>/execute/", ApprovalExecuteAPIView.as_view(), name="ops-approval-execute"),
]
