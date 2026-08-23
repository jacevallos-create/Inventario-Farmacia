from decimal import Decimal, InvalidOperation

from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.categorias.models import Categoria
from apps.farmacias.models import Farmacia, UsuarioFarmacia
from apps.inventario.models import InventarioFarmacia
from apps.laboratorios.models import Laboratorio
from apps.medicamentos.models import Medicamento
from apps.proveedores.models import Proveedor
from apps.ventas.models import Venta


def number(value, default=0):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(str(default))


def serialize_state(request):
    is_admin = request.user.is_staff or request.user.is_superuser
    pharmacies = Farmacia.objects.filter(activo=True).order_by("id")
    if not is_admin:
        pharmacies = pharmacies.filter(usuarios_asignados__usuario=request.user, usuarios_asignados__activo=True)
    branch_ids = list(pharmacies.values_list("id", flat=True))
    branches = [{
        "id": pharmacy.codigo.lower(), "name": pharmacy.nombre, "code": pharmacy.codigo,
        "address": pharmacy.direccion, "city": pharmacy.ciudad, "phone": pharmacy.telefono,
        "manager": pharmacy.administrador.get_full_name() if pharmacy.administrador else "", "active": pharmacy.activo,
    } for pharmacy in pharmacies]
    inventories = {branch["id"]: [] for branch in branches}
    inventory_rows = InventarioFarmacia.objects.filter(farmacia_id__in=branch_ids).select_related(
        "farmacia", "medicamento", "medicamento__categoria", "medicamento__laboratorio"
    )
    for row in inventory_rows:
        medicine = row.medicamento
        inventories[row.farmacia.codigo.lower()].append({
            "id": medicine.id, "name": medicine.nombre_comercial, "barcode": medicine.codigo_barras or "",
            "sku": medicine.codigo_interno, "category": medicine.categoria.nombre, "lab": medicine.laboratorio.nombre,
            "presentation": medicine.presentacion or medicine.forma_farmaceutica, "buyPrice": float(row.precio_compra),
            "sellPrice": float(row.precio_venta), "margin": float(((row.precio_venta / row.precio_compra) - 1) * 100) if row.precio_compra else 0, "min": row.stock_minimo, "stock": row.stock_actual,
        })
    suppliers = [{
        "id": supplier.id, "name": supplier.razon_social, "taxId": supplier.ruc,
        "contact": supplier.contacto, "phone": supplier.telefono, "email": supplier.correo,
        "city": supplier.ciudad, "active": supplier.activo,
    } for supplier in Proveedor.objects.filter(activo=True).order_by("id")]
    sales = [{
        "id": sale.referencia_cliente, "branchId": sale.farmacia.codigo.lower(),
        "product": sale.medicamento.nombre_comercial, "sku": sale.medicamento.codigo_interno,
        "qty": sale.cantidad, "total": float(sale.total), "customer": sale.cliente_nombre,
        "date": sale.creado_en.strftime("%d/%m/%Y, %H:%M"),
    } for sale in Venta.objects.filter(farmacia_id__in=branch_ids).select_related("farmacia", "medicamento")]
    users = []
    if is_admin:
        for user in get_user_model().objects.filter(is_active=True).order_by("id"):
            assignments = list(user.asignaciones_farmacia.filter(activo=True).select_related("farmacia"))
            users.append({
                "id": user.id, "name": user.get_full_name() or user.email.split("@")[0], "email": user.email,
                "password": "", "role": "ADMIN" if user.is_staff else (assignments[0].rol if assignments else "INVENTARIO"),
                "branchIds": [item.farmacia.codigo.lower() for item in assignments], "active": user.is_active,
            })
    return {"branches": branches, "inventories": inventories, "suppliers": suppliers, "sales": sales, "users": users}


class SystemStateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        state = serialize_state(request)
        state["empty"] = not state["branches"]
        return Response(state)

    @transaction.atomic
    def put(self, request):
        data = request.data
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Solo un administrador puede sincronizar datos."}, status=403)

        branch_map = {}
        for item in data.get("branches", []):
            code = str(item.get("id") or item.get("code") or "").strip().lower()
            if not code:
                continue
            pharmacy, _ = Farmacia.objects.update_or_create(codigo=code, defaults={
                "nombre": item.get("name") or code, "direccion": item.get("address", ""),
                "ciudad": item.get("city", ""), "telefono": item.get("phone", ""),
                "administrador": request.user, "activo": item.get("active", True),
            })
            branch_map[code] = pharmacy
            UsuarioFarmacia.objects.update_or_create(usuario=request.user, farmacia=pharmacy, defaults={"rol": UsuarioFarmacia.Rol.SUPERADMIN, "activo": True})

        for item in data.get("suppliers", []):
            ruc = str(item.get("taxId") or f"PROV-{item.get('id')}")
            Proveedor.objects.update_or_create(ruc=ruc, defaults={
                "razon_social": item.get("name") or ruc, "contacto": item.get("contact", ""),
                "telefono": item.get("phone", ""), "correo": item.get("email", ""),
                "ciudad": item.get("city", ""), "activo": item.get("active", True),
            })

        for code, items in data.get("inventories", {}).items():
            pharmacy = branch_map.get(str(code).lower()) or Farmacia.objects.filter(codigo__iexact=code).first()
            if not pharmacy:
                continue
            for item in items:
                sku = str(item.get("sku") or "").strip()
                if not sku:
                    continue
                category, _ = Categoria.objects.get_or_create(nombre=item.get("category") or "Otros")
                laboratory, _ = Laboratorio.objects.get_or_create(nombre=item.get("lab") or "Sin laboratorio")
                medicine, _ = Medicamento.objects.update_or_create(codigo_interno=sku, defaults={
                    "codigo_barras": item.get("barcode") or None, "nombre_comercial": item.get("name") or sku,
                    "presentacion": item.get("presentation", ""), "categoria": category, "laboratorio": laboratory, "activo": True,
                })
                InventarioFarmacia.objects.update_or_create(farmacia=pharmacy, medicamento=medicine, defaults={
                    "stock_actual": max(0, int(item.get("stock") or 0)), "stock_minimo": max(0, int(item.get("min") or 0)),
                    "precio_compra": max(Decimal("0"), number(item.get("buyPrice"))),
                    "precio_venta": max(Decimal("0"), number(item.get("sellPrice"))),
                })

        for item in data.get("sales", []):
            pharmacy = branch_map.get(str(item.get("branchId", "")).lower())
            medicine = Medicamento.objects.filter(codigo_interno=item.get("sku")).first()
            if pharmacy and medicine:
                qty = max(1, int(item.get("qty") or 1)); total = max(Decimal("0"), number(item.get("total")))
                Venta.objects.get_or_create(referencia_cliente=str(item.get("id")), defaults={
                    "farmacia": pharmacy, "medicamento": medicine, "usuario": request.user,
                    "cliente_nombre": item.get("customer") or "Consumidor final", "cantidad": qty,
                    "precio_unitario": total / qty, "total": total,
                })

        for item in data.get("users", []):
            email = str(item.get("email") or "").strip().lower()
            if not email:
                continue
            user, _ = get_user_model().objects.get_or_create(email=email)
            name_parts = str(item.get("name") or "").split(" ", 1)
            user.first_name = name_parts[0]; user.last_name = name_parts[1] if len(name_parts) > 1 else ""
            user.is_active = item.get("active", True); user.is_staff = item.get("role") == "ADMIN"
            if item.get("password"):
                user.set_password(item["password"])
            user.save()
            if not user.is_superuser:
                for code in item.get("branchIds", []):
                    pharmacy = branch_map.get(str(code).lower())
                    if pharmacy:
                        UsuarioFarmacia.objects.update_or_create(usuario=user, farmacia=pharmacy, defaults={"rol": item.get("role", "INVENTARIO"), "activo": True})

        return Response(serialize_state(request))


class StateRecordView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request, resource, identifier):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Solo un administrador puede eliminar registros."}, status=403)
        if resource == "inventory":
            branch = request.query_params.get("branch")
            InventarioFarmacia.objects.filter(
                farmacia__codigo__iexact=branch, medicamento_id=identifier
            ).delete()
        elif resource == "suppliers":
            Proveedor.objects.filter(pk=identifier).update(activo=False)
        elif resource == "branches":
            pharmacy = Farmacia.objects.filter(codigo__iexact=identifier).first()
            if not pharmacy:
                return Response(status=404)
            if pharmacy.inventarios.exists():
                return Response({"detail": "La sucursal todavía tiene inventario."}, status=409)
            pharmacy.activo = False
            pharmacy.save(update_fields=["activo"])
        elif resource == "users":
            user = get_user_model().objects.filter(pk=identifier).first()
            if not user:
                return Response(status=404)
            if user.pk == request.user.pk or user.is_superuser:
                return Response({"detail": "No se puede eliminar este administrador."}, status=409)
            user.is_active = False
            user.save(update_fields=["is_active"])
        else:
            return Response({"detail": "Tipo de registro desconocido."}, status=404)
        return Response(status=204)
