from decimal import Decimal, InvalidOperation
from uuid import uuid4

from django.db import transaction
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.auditoria.models import AuditLog
from apps.compras.models import Compra, CompraDetalle
from apps.cajas.models import Caja, MovimientoCaja, SesionCaja
from apps.farmacias.models import Farmacia
from apps.inventario.models import InventarioFarmacia, MovimientoInventario
from apps.lotes.models import Lote
from apps.medicamentos.models import Medicamento
from apps.proveedores.models import Proveedor
from apps.transferencias.models import Transferencia, TransferenciaDetalle


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


def serialize_transfer(row):
    return {"id": row.id, "number": row.numero, "origin": row.origen.codigo.lower(), "destination": row.destino.codigo.lower(), "status": row.estado, "user": row.solicitado_por.email, "date": timezone.localtime(row.creado_en).isoformat(), "items": [{"product": x.medicamento.nombre_comercial, "sku": x.medicamento.codigo_interno, "lot": x.lote.numero, "quantity": x.cantidad} for x in row.detalles.select_related("medicamento", "lote")]}


class TransferListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        rows = Transferencia.objects.select_related("origen", "destino", "solicitado_por").prefetch_related("detalles__medicamento", "detalles__lote")
        if not admin_user(request.user):
            rows = rows.filter(origen__usuarios_asignados__usuario=request.user, origen__usuarios_asignados__activo=True)
        return Response({"transfers": [serialize_transfer(x) for x in rows.order_by("-creado_en").distinct()]})

    @transaction.atomic
    def post(self, request):
        origin = Farmacia.objects.filter(codigo__iexact=request.data.get("origin"), activo=True).first()
        destination = Farmacia.objects.filter(codigo__iexact=request.data.get("destination"), activo=True).first()
        if not origin or not destination or origin == destination or not pharmacy_access(request.user, origin):
            return Response({"detail": "Origen o destino inválido."}, status=400)
        transfer = Transferencia.objects.create(origen=origin, destino=destination, numero=f"TR-{uuid4().hex[:10].upper()}", solicitado_por=request.user, observacion=request.data.get("notes", ""))
        for data in request.data.get("items") or []:
            lot = Lote.objects.filter(pk=data.get("lotId"), farmacia=origin, cantidad_disponible__gt=0).select_related("medicamento").first()
            try: quantity = int(data.get("quantity", 0))
            except (TypeError, ValueError): quantity = 0
            if not lot or quantity < 1 or quantity > lot.cantidad_disponible or lot.fecha_vencimiento < timezone.localdate():
                transaction.set_rollback(True); return Response({"detail": "Lote o cantidad inválida para transferir."}, status=409)
            TransferenciaDetalle.objects.create(transferencia=transfer, medicamento=lot.medicamento, lote=lot, cantidad=quantity)
        if not transfer.detalles.exists():
            transaction.set_rollback(True); return Response({"detail": "La transferencia requiere productos."}, status=400)
        audit(request, AuditLog.Accion.CREAR, "transferencia", transfer, f"Transferencia {transfer.numero} solicitada", origin)
        return Response(serialize_transfer(transfer), status=201)


class TransferActionView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request, transfer_id, action):
        transfer = Transferencia.objects.select_for_update().select_related("origen", "destino").filter(pk=transfer_id).first()
        if not transfer or not admin_user(request.user): return Response({"detail": "Transferencia no disponible."}, status=403)
        if action == "approve" and transfer.estado == Transferencia.Estado.SOLICITADA:
            transfer.estado = Transferencia.Estado.APROBADA; transfer.aprobado_por = request.user
        elif action == "dispatch" and transfer.estado == Transferencia.Estado.APROBADA:
            for detail in transfer.detalles.select_related("lote", "medicamento"):
                lot = Lote.objects.select_for_update().get(pk=detail.lote_id)
                inventory = InventarioFarmacia.objects.select_for_update().get(farmacia=transfer.origen, medicamento=detail.medicamento)
                if lot.fecha_vencimiento < timezone.localdate() or lot.cantidad_disponible < detail.cantidad or inventory.stock_actual < detail.cantidad:
                    return Response({"detail": "Stock o lote no disponible para despacho."}, status=409)
                previous = inventory.stock_actual; lot.cantidad_disponible -= detail.cantidad; inventory.stock_actual -= detail.cantidad; lot.save(); inventory.save()
                MovimientoInventario.objects.create(farmacia=transfer.origen, medicamento=detail.medicamento, lote=lot, tipo="SALIDA", concepto="TRANSFERENCIA", cantidad=detail.cantidad, saldo_anterior=previous, saldo_nuevo=inventory.stock_actual, costo_unitario=lot.costo_unitario, documento_tipo="TRANSFERENCIA", documento_id=transfer.id, usuario=request.user)
            transfer.estado = Transferencia.Estado.TRANSITO
        elif action == "receive" and transfer.estado == Transferencia.Estado.TRANSITO:
            for detail in transfer.detalles.select_related("lote", "medicamento"):
                source = detail.lote
                lot, _ = Lote.objects.select_for_update().get_or_create(farmacia=transfer.destino, medicamento=detail.medicamento, numero=source.numero, defaults={"proveedor": source.proveedor, "fecha_fabricacion": source.fecha_fabricacion, "fecha_vencimiento": source.fecha_vencimiento, "cantidad_inicial": 0, "cantidad_disponible": 0, "costo_unitario": source.costo_unitario})
                inventory, _ = InventarioFarmacia.objects.select_for_update().get_or_create(farmacia=transfer.destino, medicamento=detail.medicamento)
                previous = inventory.stock_actual; lot.cantidad_inicial += detail.cantidad; lot.cantidad_disponible += detail.cantidad; inventory.stock_actual += detail.cantidad; lot.save(); inventory.save()
                MovimientoInventario.objects.create(farmacia=transfer.destino, medicamento=detail.medicamento, lote=lot, tipo="ENTRADA", concepto="TRANSFERENCIA", cantidad=detail.cantidad, saldo_anterior=previous, saldo_nuevo=inventory.stock_actual, costo_unitario=lot.costo_unitario, documento_tipo="TRANSFERENCIA", documento_id=transfer.id, usuario=request.user)
            transfer.estado = Transferencia.Estado.RECIBIDA
        else: return Response({"detail": "La acción no corresponde al estado actual."}, status=409)
        transfer.save(); audit(request, AuditLog.Accion.MODIFICAR, "transferencia", transfer, f"Transferencia {transfer.numero}: {transfer.estado}", transfer.origen)
        return Response(serialize_transfer(transfer))


def serialize_cash_session(session):
    movements = session.movimientos.select_related("usuario").order_by("creado_en")
    signed = sum((x.monto if x.tipo in (MovimientoCaja.Tipo.VENTA, MovimientoCaja.Tipo.INGRESO) else -x.monto) for x in movements)
    expected = session.saldo_inicial + signed
    return {"id": session.id, "cashbox": session.caja.nombre, "branchId": session.caja.farmacia.codigo.lower(), "user": session.usuario.email, "opened": timezone.localtime(session.abierta_en).isoformat(), "closed": timezone.localtime(session.cerrada_en).isoformat() if session.cerrada_en else None, "initial": float(session.saldo_inicial), "expected": float(expected), "declared": float(session.saldo_final_declarado) if session.saldo_final_declarado is not None else None, "difference": float(session.saldo_final_declarado - expected) if session.saldo_final_declarado is not None else None, "movements": [{"id": x.id, "type": x.tipo, "payment": x.forma_pago, "amount": float(x.monto), "reference": x.referencia, "notes": x.observacion, "date": timezone.localtime(x.creado_en).isoformat(), "user": x.usuario.email} for x in movements]}


class CashSessionView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        branch = request.query_params.get("branch")
        session = SesionCaja.objects.filter(caja__farmacia__codigo__iexact=branch, usuario=request.user, cerrada_en__isnull=True).select_related("caja", "caja__farmacia", "usuario").first()
        return Response({"session": serialize_cash_session(session) if session else None})
    @transaction.atomic
    def post(self, request):
        pharmacy = Farmacia.objects.filter(codigo__iexact=request.data.get("branchId"), activo=True).first()
        if not pharmacy or not pharmacy_access(request.user, pharmacy): return Response({"detail": "Sucursal no autorizada."}, status=403)
        if SesionCaja.objects.filter(usuario=request.user, cerrada_en__isnull=True).exists(): return Response({"detail": "Ya tienes una caja abierta."}, status=409)
        initial = decimal_value(request.data.get("initial"))
        if initial < 0: return Response({"detail": "El saldo inicial no es válido."}, status=400)
        cashbox, _ = Caja.objects.get_or_create(farmacia=pharmacy, nombre=request.data.get("name") or "Caja principal")
        session = SesionCaja.objects.create(caja=cashbox, usuario=request.user, saldo_inicial=initial)
        audit(request, AuditLog.Accion.CREAR, "caja", session, f"Apertura de {cashbox.nombre}", pharmacy, {"saldo_inicial": str(initial)})
        return Response(serialize_cash_session(session), status=201)


class CashMovementView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request, session_id):
        session = SesionCaja.objects.select_for_update().select_related("caja", "caja__farmacia", "usuario").filter(pk=session_id, usuario=request.user, cerrada_en__isnull=True).first()
        amount = decimal_value(request.data.get("amount")); movement_type = request.data.get("type")
        if not session or amount <= 0 or movement_type not in MovimientoCaja.Tipo.values: return Response({"detail": "Movimiento inválido o caja cerrada."}, status=409)
        movement = MovimientoCaja.objects.create(sesion=session, tipo=movement_type, forma_pago=request.data.get("payment") or "EFECTIVO", monto=amount, referencia=request.data.get("reference", ""), observacion=request.data.get("notes", ""), usuario=request.user)
        audit(request, AuditLog.Accion.CREAR, "movimiento_caja", movement, f"{movement_type} en {session.caja.nombre}", session.caja.farmacia, {"monto": str(amount)})
        return Response(serialize_cash_session(session), status=201)


class CashCloseView(APIView):
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request, session_id):
        session = SesionCaja.objects.select_for_update().select_related("caja", "caja__farmacia", "usuario").filter(pk=session_id, usuario=request.user, cerrada_en__isnull=True).first()
        declared = decimal_value(request.data.get("declared"))
        if not session or declared < 0: return Response({"detail": "Caja o saldo declarado inválido."}, status=409)
        movements = session.movimientos.all(); signed = sum((x.monto if x.tipo in (MovimientoCaja.Tipo.VENTA, MovimientoCaja.Tipo.INGRESO) else -x.monto) for x in movements)
        session.saldo_final_sistema = session.saldo_inicial + signed; session.saldo_final_declarado = declared; session.cerrada_en = timezone.now(); session.save()
        audit(request, AuditLog.Accion.MODIFICAR, "caja", session, f"Cierre de {session.caja.nombre}", session.caja.farmacia, {"esperado": str(session.saldo_final_sistema), "declarado": str(declared), "diferencia": str(declared - session.saldo_final_sistema)})
        return Response(serialize_cash_session(session))
