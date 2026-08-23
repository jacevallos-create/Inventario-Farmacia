from django.core.validators import MinValueValidator
from django.db import models
from apps.core.models import TimeStampedModel


class Lote(TimeStampedModel):
    medicamento = models.ForeignKey("medicamentos.Medicamento", on_delete=models.PROTECT, related_name="lotes")
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="lotes")
    proveedor = models.ForeignKey("proveedores.Proveedor", null=True, blank=True, on_delete=models.PROTECT, related_name="lotes")
    numero = models.CharField(max_length=80)
    fecha_fabricacion = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(db_index=True)
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    costo_unitario = models.DecimalField(max_digits=12, decimal_places=4, validators=[MinValueValidator(0)])
    class Meta:
        constraints = [models.UniqueConstraint(fields=["farmacia", "medicamento", "numero"], name="uq_lote_farmacia_medicamento_numero")]
        indexes = [models.Index(fields=["farmacia", "fecha_vencimiento", "cantidad_disponible"])]

