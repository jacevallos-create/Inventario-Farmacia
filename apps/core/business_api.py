from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import AuditLog
from apps.compras.models import Compra, CompraDetalle
from apps.farmacias.models import Farmacia
from apps.inventario.models import InventarioFarmacia, MovimientoInventario
from apps.lotes.models import Lote
from apps.medicamentos.models import Medicamento
from apps.proveedores.models import Proveedor


def admin_user(user):
    return user.is_staff or user.is_superuser


def pharmacy_access(user, pharmacy):
    return admin_user(user) or user.asignaciones_farmacia.filter(farmacia=pharmacy, activo=True).exists()


def decimal_value(value):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("-1")


def audit(request, action, entity, instance, description, pharmacy, changes=None):
    AuditLog.objects.create(
        usuario=request.user, farmacia=pharmacy, accion=action, entidad=entity,
        objeto_id=str(instance.pk), descripcion=description, cambios=changes or {},
        ip=(request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")),
    )


def serialize_purchase(purchase):
    return {
        "id": purchase.id, "number": purchase.numero, "branchId": purchase.farmacia.codigo.lower(),
        "supplierId": purchase.proveedor_id, "supplier": purchase.proveedor.razon_social,
        "status": purchase.estado, "total": float(purchase.total), "user": purchase.usuario.email,
        "date": timezone.localtime(purchase.creado_en).isoformat(), "notes": purchase.observacion,
        "items": [{
            "id": item.id, "productId": item.medicamento_id, "sku": item.medicamento.codigo_interno,
            "product": item.medicamento.nombre_comercial, "ordered": item.cantidad_solicitada,
            "received": item.cantidad_recibida, "cost": float(item.costo_unitario),
        } for item in purchase.detalles.select_related("medicamento")],
    }


class PurchaseListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = Compra.objects.select_related("farmacia", "proveedor", "usuario").prefetch_related("detalles__medicamento")
        if not admin_user(request.user):
            rows = rows.filter(farmacia__usuarios_asignados__usuario=request.user, farmacia__usuarios_asignados__activo=True)
        return Response({"purchases": [serialize_purchase(row) for row in rows.order_by("-creado_en")]})

    @transaction.atomic
    def post(self, request):
        if not admin_user(request.user):
            return Response({"detail": "Solo administradores pueden crear órdenes de compra."}, status=403)
        pharmacy = Farmacia.objects.filter(codigo__iexact=request.data.get("branchId"), activo=True).first()
        supplier = Proveedor.objects.filter(pk=request.data.get("supplierId"), activo=True).first()
        items = request.data.get("items") or []
        if not pharmacy or not supplier or not items:
            return Response({"detail": "Sucursal, proveedor y productos son obligatorios."}, status=400)
        purchase = Compra.objects.create(
            farmacia=pharmacy, proveedor=supplier, numero=request.data.get("number") or f"OC-{uuid4().hex[:10].upper()}",
            estado=Compra.Estado.ORDENADA, usuario=request.user, observacion=request.data.get("notes", ""),
        )
        total = Decimal("0")
        for data in items:
            medicine = Medicamento.objects.filter(pk=data.get("productId"), activo=True).first()
            try:
                quantity = int(data.get("quantity", 0))
            except (TypeError, ValueError):
                quantity = 0
            cost = decimal_value(data.get("cost"))
            if not medicine or quantity < 1 or cost < 0:
                transaction.set_rollback(True)
                return Response({"detail": "Existe un producto, cantidad o costo inválido."}, status=400)
            CompraDetalle.objects.create(compra=purchase, medicamento=medicine, cantidad_solicitada=quantity, costo_unitario=cost)
            total += cost * quantity
        purchase.total = total; purchase.save(update_fields=["total", "actualizado_en"])
        audit(request, AuditLog.Accion.CREAR, "compra", purchase, f"Orden {purchase.numero} creada", pharmacy, {"total": str(total)})
        return Response(serialize_purchase(purchase), status=201)


class PurchaseReceiveView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, purchase_id):
        if not admin_user(request.user):
            return Response({"detail": "Solo administradores pueden recibir compras."}, status=403)
        purchase = Compra.objects.select_for_update().select_related("farmacia", "proveedor", "usuario").filter(pk=purchase_id).first()
        if not purchase or purchase.estado in (Compra.Estado.RECIBIDA, Compra.Estado.ANULADA):
            return Response({"detail": "La orden no está disponible para recepción."}, status=409)
        receptions = request.data.get("items") or []
        if not receptions:
            return Response({"detail": "Debes indicar los lotes recibidos."}, status=400)
        today = timezone.localdate()
        received_log = []
        for data in receptions:
            detail = CompraDetalle.objects.select_for_update().select_related("medicamento").filter(pk=data.get("detailId"), compra=purchase).first()
            try:
                quantity = int(data.get("quantity", 0))
                expires = timezone.datetime.fromisoformat(str(data.get("expires"))).date()
            except (TypeError, ValueError):
                return Response({"detail": "Cantidad o vencimiento inválido."}, status=400)
            pending = detail.cantidad_solicitada - detail.cantidad_recibida if detail else 0
            if not detail or quantity < 1 or quantity > pending or expires <= today:
                return Response({"detail": "La recepción excede lo pendiente o el lote está vencido."}, status=409)
            lot_number = str(data.get("lot") or "").strip()
            if not lot_number:
                return Response({"detail": "El número de lote es obligatorio."}, status=400)
            lot, created = Lote.objects.select_for_update().get_or_create(
                farmacia=purchase.farmacia, medicamento=detail.medicamento, numero=lot_number,
                defaults={"proveedor": purchase.proveedor, "fecha_vencimiento": expires, "cantidad_inicial": 0, "cantidad_disponible": 0, "costo_unitario": detail.costo_unitario},
            )
            if not created and lot.fecha_vencimiento != expires:
                return Response({"detail": f"El lote {lot_number} ya existe con otro vencimiento."}, status=409)
            lot.cantidad_inicial += quantity; lot.cantidad_disponible += quantity
            lot.costo_unitario = detail.costo_unitario; lot.save()
            inventory, _ = InventarioFarmacia.objects.select_for_update().get_or_create(farmacia=purchase.farmacia, medicamento=detail.medicamento)
            previous = inventory.stock_actual; inventory.stock_actual += quantity; inventory.precio_compra = detail.costo_unitario; inventory.save()
            MovimientoInventario.objects.create(
                farmacia=purchase.farmacia, medicamento=detail.medicamento, lote=lot,
                tipo=MovimientoInventario.Tipo.ENTRADA, concepto="COMPRA", cantidad=quantity,
                saldo_anterior=previous, saldo_nuevo=inventory.stock_actual, costo_unitario=detail.costo_unitario,
                documento_tipo="COMPRA", documento_id=purchase.id, usuario=request.user,
                observacion=f"Recepción de {purchase.numero}",
            )
            detail.cantidad_recibida += quantity; detail.save(update_fields=["cantidad_recibida", "actualizado_en"])
            received_log.append({"sku": detail.medicamento.codigo_interno, "lot": lot.numero, "quantity": quantity, "expires": expires.isoformat()})
        details = list(purchase.detalles.all())
        purchase.estado = Compra.Estado.RECIBIDA if all(x.cantidad_recibida == x.cantidad_solicitada for x in details) else Compra.Estado.PARCIAL
        purchase.save(update_fields=["estado", "actualizado_en"])
        audit(request, AuditLog.Accion.MODIFICAR, "compra", purchase, f"Recepción de {purchase.numero}", purchase.farmacia, {"lotes": received_log})
        return Response(serialize_purchase(purchase))
