from django.contrib.auth import logout
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response({"status": "ok", "api": "v1"})


@method_decorator(ensure_csrf_cookie, name="dispatch")
class SessionView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"authenticated": False})
        assignments = request.user.asignaciones_farmacia.filter(activo=True).select_related("farmacia")
        branch_ids = [assignment.farmacia.codigo.lower() for assignment in assignments]
        is_admin = request.user.is_staff or request.user.is_superuser
        return Response({
            "authenticated": True,
            "user": {
                "id": request.user.pk,
                "name": request.user.get_full_name() or request.user.email.split("@")[0],
                "email": request.user.email,
                "role": "ADMIN" if is_admin else "INVENTARIO",
                "branchIds": branch_ids or (["central"] if not is_admin else []),
                "active": request.user.is_active,
            },
        })


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({"ok": True})


urlpatterns = [
    path("health/", HealthView.as_view(), name="api-health"),
    path("auth/session/", SessionView.as_view(), name="api-session"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
]
