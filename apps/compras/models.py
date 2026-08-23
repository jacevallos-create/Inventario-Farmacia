from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from apps.core.models import TimeStampedModel


class Compra(TimeStampedModel):
    class Estado(models.TextChoices):
        BORRADOR = "BORRADOR", "Borrador"
        ORDENADA = "ORDENADA", "Ordenada"
        PARCIAL = "PARCIAL", "Recibida parcialmente"
        RECIBIDA = "RECIBIDA", "Recibida"
        ANULADA = "ANULADA", "Anulada"
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="compras")
    proveedor = models.ForeignKey("proveedores.Proveedor", on_delete=models.PROTECT, related_name="compras")
    numero = models.CharField(max_length=40, unique=True)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.BORRADOR)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="compras")
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    observacion = models.TextField(blank=True)


class CompraDetalle(TimeStampedModel):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name="detalles")
    medicamento = models.ForeignKey("medicamentos.Medicamento", on_delete=models.PROTECT)
    cantidad_solicitada = models.PositiveIntegerField()
    cantidad_recibida = models.PositiveIntegerField(default=0)
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(0)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=["compra", "medicamento"], name="uq_compra_medicamento")]


class DevolucionProveedor(TimeStampedModel):
    compra = models.ForeignKey(Compra, on_delete=models.PROTECT, related_name="devoluciones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    autorizada_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="devoluciones_proveedor_autorizadas")
    motivo = models.CharField(max_length=255)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)


class DevolucionProveedorDetalle(TimeStampedModel):
    devolucion = models.ForeignKey(DevolucionProveedor, on_delete=models.CASCADE, related_name="detalles")
    lote = models.ForeignKey("lotes.Lote", on_delete=models.PROTECT, related_name="devoluciones_proveedor")
    cantidad = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(0)])
