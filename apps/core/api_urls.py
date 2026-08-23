from django.urls import path
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "api": "v1"})


urlpatterns = [path("health/", HealthView.as_view(), name="api-health")]
