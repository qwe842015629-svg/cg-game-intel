from __future__ import annotations

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .feishu_bot import handle_feishu_event_callback


class FeishuEventWebhookAPIView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        status_code, body = handle_feishu_event_callback(payload)
        return Response(body, status=status_code)
