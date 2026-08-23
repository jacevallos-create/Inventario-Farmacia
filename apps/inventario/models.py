from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from apps.core.models import TimeStampedModel


class InventarioFarmacia(TimeStampedModel):
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="inventarios")
    medicamento = models.ForeignKey("medicamentos.Medicamento", on_delete=models.PROTECT, related_name="inventarios")
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=0)
    stock_maximo = models.PositiveIntegerField(null=True, blank=True)
    ubicacion = models.CharField(max_length=100, blank=True)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=["farmacia", "medicamento"], name="uq_inventario_farmacia_medicamento")]
        indexes = [models.Index(fields=["farmacia", "stock_actual"])]


class MovimientoInventario(TimeStampedModel):
    class Tipo(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SALIDA = "SALIDA", "Salida"
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="movimientos_inventario")
    medicamento = models.ForeignKey("medicamentos.Medicamento", on_delete=models.PROTECT, related_name="movimientos")
    lote = models.ForeignKey("lotes.Lote", null=True, blank=True, on_delete=models.PROTECT, related_name="movimientos")
    tipo = models.CharField(max_length=10, choices=Tipo.choices)
    concepto = models.CharField(max_length=30)
    cantidad = models.PositiveIntegerField()
    saldo_anterior = models.PositiveIntegerField()
    saldo_nuevo = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    documento_tipo = models.CharField(max_length=40, blank=True)
    documento_id = models.PositiveBigIntegerField(null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    observacion = models.TextField(blank=True)
    class Meta:
        indexes = [models.Index(fields=["farmacia", "medicamento", "creado_en"])]


class HistorialPrecio(TimeStampedModel):
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT)
    medicamento = models.ForeignKey("medicamentos.Medicamento", on_delete=models.PROTECT)
    precio_anterior = models.DecimalField(max_digits=12, decimal_places=2)
    precio_nuevo = models.DecimalField(max_digits=12, decimal_places=2)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    motivo = models.CharField(max_length=255)

