from django.contrib.auth import authenticate, login as auth_login, logout
from django.urls import path
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .state_api import StateRecordView, SystemStateView
from .operations_api import CustomerReturnView, DashboardView, ExcelReportView, LotAlertsView, SaleCancelView, SaleCreateView
from .business_api import AvailableLotsView, CashCloseView, CashMovementView, CashSessionView, PurchaseCancelView, PurchaseListCreateView, PurchaseReceiveView, SupplierReturnView, TransferActionView, TransferListCreateView


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
        primary_assignment = assignments.first()
        return Response({
            "authenticated": True,
            "user": {
                "id": request.user.pk,
                "name": request.user.get_full_name() or request.user.email.split("@")[0],
                "email": request.user.email,
                "role": "ADMIN" if is_admin else (primary_assignment.rol if primary_assignment else "CONSULTA"),
                "branchIds": branch_ids or (["central"] if not is_admin else []),
                "active": request.user.is_active,
            },
        })


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({"ok": True})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        password = str(request.data.get("password", ""))
        user = authenticate(request, email=email, password=password)
        if user is None or not user.is_active:
            return Response({"detail": "Correo o contraseña incorrectos."}, status=400)
        auth_login(request, user)
        assignments = user.asignaciones_farmacia.filter(activo=True).select_related("farmacia")
        branch_ids = [assignment.farmacia.codigo.lower() for assignment in assignments]
        is_admin = user.is_staff or user.is_superuser
        primary_assignment = assignments.first()
        return Response({"authenticated": True, "user": {
            "id": user.pk,
            "name": user.get_full_name() or user.email.split("@")[0],
            "email": user.email,
            "role": "ADMIN" if is_admin else (primary_assignment.rol if primary_assignment else "CONSULTA"),
            "branchIds": branch_ids or (["central"] if not is_admin else []),
            "active": user.is_active,
        }})


urlpatterns = [
    path("health/", HealthView.as_view(), name="api-health"),
    path("auth/session/", SessionView.as_view(), name="api-session"),
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),
    path("state/", SystemStateView.as_view(), name="api-state"),
    path("state/<str:resource>/<str:identifier>/", StateRecordView.as_view(), name="api-state-record"),
    path("sales/", SaleCreateView.as_view(), name="api-sales"),
    path("sales/<str:sale_id>/cancel/", SaleCancelView.as_view(), name="api-sale-cancel"),
    path("sales/<str:sale_id>/return/", CustomerReturnView.as_view(), name="api-sale-return"),
    path("lots/alerts/", LotAlertsView.as_view(), name="api-lot-alerts"),
    path("reports/excel/", ExcelReportView.as_view(), name="api-excel-report"),
    path("dashboard/", DashboardView.as_view(), name="api-dashboard"),
    path("purchases/", PurchaseListCreateView.as_view(), name="api-purchases"),
    path("purchases/<int:purchase_id>/receive/", PurchaseReceiveView.as_view(), name="api-purchase-receive"),
    path("purchases/<int:purchase_id>/cancel/", PurchaseCancelView.as_view(), name="api-purchase-cancel"),
    path("purchases/<int:purchase_id>/return/", SupplierReturnView.as_view(), name="api-supplier-return"),
    path("transfers/", TransferListCreateView.as_view(), name="api-transfers"),
    path("transfers/lots/", AvailableLotsView.as_view(), name="api-transfer-lots"),
    path("transfers/<int:transfer_id>/<str:action>/", TransferActionView.as_view(), name="api-transfer-action"),
    path("cash/session/", CashSessionView.as_view(), name="api-cash-session"),
    path("cash/session/<int:session_id>/movement/", CashMovementView.as_view(), name="api-cash-movement"),
    path("cash/session/<int:session_id>/close/", CashCloseView.as_view(), name="api-cash-close"),
]
