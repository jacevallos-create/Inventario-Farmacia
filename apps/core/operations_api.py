from io import BytesIO
from datetime import timedelta
from uuid import uuid4

from django.db import transaction
from django.http import HttpResponse
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import AuditLog
from apps.farmacias.models import Farmacia
from apps.inventario.models import InventarioFarmacia, MovimientoInventario
from apps.lotes.models import Lote
from apps.ventas.models import Venta, VentaLote


def audit(request, action, entity, instance, description, pharmacy=None, changes=None):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    AuditLog.objects.create(
        usuario=request.user, farmacia=pharmacy, accion=action, entidad=entity,
        objeto_id=str(instance.pk), descripcion=description, cambios=changes or {},
        ip=forwarded or request.META.get("REMOTE_ADDR"),
    )


class SaleCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        branch_code = str(request.data.get("branchId", "")).strip()
        medicine_id = request.data.get("productId")
        try:
            quantity = int(request.data.get("qty", 0))
        except (TypeError, ValueError):
            quantity = 0
        if quantity < 1:
            return Response({"detail": "La cantidad debe ser mayor que cero."}, status=400)

        pharmacy = Farmacia.objects.filter(codigo__iexact=branch_code, activo=True).first()
        if not pharmacy:
            return Response({"detail": "La sucursal no existe o está inactiva."}, status=404)
        if not (request.user.is_staff or request.user.is_superuser or request.user.asignaciones_farmacia.filter(farmacia=pharmacy, activo=True).exists()):
            return Response({"detail": "No tienes acceso a esta sucursal."}, status=403)

        inventory = InventarioFarmacia.objects.select_for_update().select_related("medicamento").filter(
            farmacia=pharmacy, medicamento_id=medicine_id
        ).first()
        if not inventory or inventory.stock_actual < quantity:
            return Response({"detail": "No hay existencias suficientes."}, status=409)

        today = timezone.localdate()
        lots = list(Lote.objects.select_for_update().filter(
            farmacia=pharmacy, medicamento_id=medicine_id,
            cantidad_disponible__gt=0, fecha_vencimiento__gte=today,
        ).order_by("fecha_vencimiento", "id"))
        if sum(item.cantidad_disponible for item in lots) < quantity:
            return Response({"detail": "No hay lotes vigentes suficientes. Los lotes vencidos están bloqueados."}, status=409)

        reference = str(request.data.get("reference") or uuid4().hex)
        sale = Venta.objects.create(
            referencia_cliente=reference, farmacia=pharmacy, medicamento=inventory.medicamento,
            usuario=request.user, cliente_nombre=request.data.get("customer") or "Consumidor final",
            cantidad=quantity, precio_unitario=inventory.precio_venta,
            total=inventory.precio_venta * quantity,
        )
        remaining = quantity
        previous_total = inventory.stock_actual
        consumed = []
        for lot in lots:
            if not remaining:
                break
            used = min(remaining, lot.cantidad_disponible)
            lot.cantidad_disponible -= used
            lot.save(update_fields=["cantidad_disponible", "actualizado_en"])
            VentaLote.objects.create(venta=sale, lote=lot, cantidad=used, precio_unitario=inventory.precio_venta)
            MovimientoInventario.objects.create(
                farmacia=pharmacy, medicamento=inventory.medicamento, lote=lot,
                tipo=MovimientoInventario.Tipo.SALIDA, concepto="VENTA", cantidad=used,
                saldo_anterior=previous_total, saldo_nuevo=previous_total - used,
                costo_unitario=lot.costo_unitario, documento_tipo="VENTA", documento_id=sale.pk,
                usuario=request.user, observacion=f"Venta {reference} por FEFO",
            )
            previous_total -= used
            remaining -= used
            consumed.append({"number": lot.numero, "quantity": used, "expires": lot.fecha_vencimiento.isoformat()})

        inventory.stock_actual -= quantity
        inventory.save(update_fields=["stock_actual", "actualizado_en"])
        audit(request, AuditLog.Accion.CREAR, "venta", sale, f"Venta {reference}", pharmacy, {"cantidad": quantity, "lotes": consumed})
        return Response({
            "sale": {"id": sale.referencia_cliente, "branchId": pharmacy.codigo.lower(),
                     "product": inventory.medicamento.nombre_comercial, "sku": inventory.medicamento.codigo_interno,
                     "qty": quantity, "total": float(sale.total), "customer": sale.cliente_nombre,
                     "date": timezone.localtime(sale.creado_en).strftime("%d/%m/%Y, %H:%M"), "lots": consumed,
                     "user": request.user.email},
            "stock": inventory.stock_actual,
        }, status=201)


class LotAlertsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        days = min(max(int(request.query_params.get("days", 90)), 1), 365)
        rows = Lote.objects.filter(cantidad_disponible__gt=0).select_related("farmacia", "medicamento")
        if not (request.user.is_staff or request.user.is_superuser):
            rows = rows.filter(farmacia__usuarios_asignados__usuario=request.user, farmacia__usuarios_asignados__activo=True)
        data = [{
            "id": lot.id, "branchId": lot.farmacia.codigo.lower(), "sku": lot.medicamento.codigo_interno,
            "product": lot.medicamento.nombre_comercial, "number": lot.numero,
            "expires": lot.fecha_vencimiento.isoformat(), "quantity": lot.cantidad_disponible,
            "status": "EXPIRED" if lot.fecha_vencimiento < today else "EXPIRING",
        } for lot in rows.filter(fecha_vencimiento__lte=today + timedelta(days=days)).order_by("fecha_vencimiento")]
        return Response({"lots": data})


class ExcelReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({"detail": "Solo administradores pueden exportar reportes."}, status=403)
        branch = request.query_params.get("branch")
        date_from = request.query_params.get("from")
        date_to = request.query_params.get("to")
        user = request.query_params.get("user")
        movement_type = request.query_params.get("movement")

        inventories = InventarioFarmacia.objects.select_related("farmacia", "medicamento")
        sales = Venta.objects.select_related("farmacia", "medicamento", "usuario").prefetch_related("lotes_consumidos__lote")
        movements = MovimientoInventario.objects.select_related("farmacia", "medicamento", "lote", "usuario")
        if branch and branch != "ALL":
            inventories = inventories.filter(farmacia__codigo__iexact=branch)
            sales = sales.filter(farmacia__codigo__iexact=branch)
            movements = movements.filter(farmacia__codigo__iexact=branch)
        if date_from:
            sales = sales.filter(creado_en__date__gte=date_from); movements = movements.filter(creado_en__date__gte=date_from)
        if date_to:
            sales = sales.filter(creado_en__date__lte=date_to); movements = movements.filter(creado_en__date__lte=date_to)
        if user:
            sales = sales.filter(usuario_id=user); movements = movements.filter(usuario_id=user)
        if movement_type:
            movements = movements.filter(tipo=movement_type)

        workbook = Workbook(); inventory_sheet = workbook.active; inventory_sheet.title = "Inventario"
        self._sheet(inventory_sheet, ["Sucursal", "SKU", "Medicamento", "Stock", "Mínimo", "Compra", "Venta"], [
            [x.farmacia.nombre, x.medicamento.codigo_interno, x.medicamento.nombre_comercial, x.stock_actual, x.stock_minimo, x.precio_compra, x.precio_venta] for x in inventories
        ])
        sale_sheet = workbook.create_sheet("Ventas")
        self._sheet(sale_sheet, ["Fecha", "Sucursal", "Referencia", "Usuario", "Medicamento", "Lotes FEFO", "Cantidad", "Precio", "Total"], [
            [timezone.localtime(x.creado_en).strftime("%Y-%m-%d %H:%M"), x.farmacia.nombre, x.referencia_cliente, x.usuario.email,
             x.medicamento.nombre_comercial, ", ".join(f"{d.lote.numero} ({d.cantidad})" for d in x.lotes_consumidos.all()), x.cantidad, x.precio_unitario, x.total] for x in sales
        ])
        movement_sheet = workbook.create_sheet("Movimientos")
        self._sheet(movement_sheet, ["Fecha", "Sucursal", "Tipo", "Concepto", "Usuario", "Medicamento", "Lote", "Cantidad", "Saldo anterior", "Saldo nuevo"], [
            [timezone.localtime(x.creado_en).strftime("%Y-%m-%d %H:%M"), x.farmacia.nombre, x.tipo, x.concepto, x.usuario.email,
             x.medicamento.nombre_comercial, x.lote.numero if x.lote else "", x.cantidad, x.saldo_anterior, x.saldo_nuevo] for x in movements
        ])
        stream = BytesIO(); workbook.save(stream)
        response = HttpResponse(stream.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="reporte-supabase-{today_string()}.xlsx"'
        return response

    @staticmethod
    def _sheet(sheet, headers, rows):
        sheet.append(headers)
        for cell in sheet[1]:
            cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="2563EB")
        for row in rows:
            sheet.append(row)
        sheet.freeze_panes = "A2"; sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            sheet.column_dimensions[column[0].column_letter].width = min(max(len(str(c.value or "")) for c in column) + 2, 45)


def today_string():
    return timezone.localdate().isoformat()
