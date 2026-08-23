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
