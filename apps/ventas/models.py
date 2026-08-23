from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import TimeStampedModel


class Venta(TimeStampedModel):
    referencia_cliente = models.CharField(max_length=64, unique=True)
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="ventas")
    medicamento = models.ForeignKey("medicamentos.Medicamento", on_delete=models.PROTECT, related_name="ventas")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="ventas")
    cliente_nombre = models.CharField(max_length=180, default="Consumidor final")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    forma_pago = models.CharField(max_length=20, choices=[("EFECTIVO", "Efectivo"), ("TARJETA", "Tarjeta"), ("TRANSFERENCIA", "Transferencia")], default="EFECTIVO")
    sesion_caja = models.ForeignKey("cajas.SesionCaja", null=True, blank=True, on_delete=models.PROTECT, related_name="ventas")
    anulada = models.BooleanField(default=False, db_index=True)
    anulada_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="ventas_anuladas")
    anulada_en = models.DateTimeField(null=True, blank=True)
    motivo_anulacion = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-creado_en"]
        indexes = [models.Index(fields=["farmacia", "creado_en"])]


class VentaLote(TimeStampedModel):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="lotes_consumidos")
    lote = models.ForeignKey("lotes.Lote", on_delete=models.PROTECT, related_name="detalles_venta")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["venta", "lote"], name="uq_venta_lote")]


class DevolucionVenta(TimeStampedModel):
    venta = models.ForeignKey(Venta, on_delete=models.PROTECT, related_name="devoluciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    motivo = models.CharField(max_length=255)
    autorizada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="devoluciones_autorizadas")
    total_devuelto = models.DecimalField(max_digits=14, decimal_places=2)


class DevolucionVentaLote(TimeStampedModel):
    devolucion = models.ForeignKey(DevolucionVenta, on_delete=models.CASCADE, related_name="lotes_repuestos")
    lote = models.ForeignKey("lotes.Lote", on_delete=models.PROTECT, related_name="devoluciones_cliente")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])


class ComprobanteElectronico(TimeStampedModel):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        FIRMADO = "FIRMADO", "Firmado"
        AUTORIZADO = "AUTORIZADO", "Autorizado"
        DEVUELTO = "DEVUELTO", "Devuelto"
        ANULADO = "ANULADO", "Anulado"
    venta = models.OneToOneField(Venta, on_delete=models.PROTECT, related_name="comprobante")
    clave_acceso = models.CharField(max_length=49, unique=True)
    secuencial = models.CharField(max_length=9)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PENDIENTE)
    xml_generado = models.TextField(blank=True)
    xml_autorizado = models.TextField(blank=True)
    numero_autorizacion = models.CharField(max_length=64, blank=True)
    autorizado_en = models.DateTimeField(null=True, blank=True)
    mensajes_sri = models.JSONField(default=list, blank=True)


class NotaCredito(TimeStampedModel):
    devolucion = models.OneToOneField(DevolucionVenta, on_delete=models.PROTECT, related_name="nota_credito")
    numero = models.CharField(max_length=30, unique=True)
    motivo = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    estado = models.CharField(max_length=15, choices=[("GENERADA", "Generada"), ("AUTORIZADA", "Autorizada"), ("ANULADA", "Anulada")], default="GENERADA")
    clave_acceso = models.CharField(max_length=49, blank=True)
