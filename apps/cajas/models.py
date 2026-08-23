from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel


class Caja(TimeStampedModel):
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="cajas")
    nombre = models.CharField(max_length=80)
    activa = models.BooleanField(default=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["farmacia", "nombre"], name="uq_caja_farmacia_nombre")]


class SesionCaja(TimeStampedModel):
    caja = models.ForeignKey(Caja, on_delete=models.PROTECT, related_name="sesiones")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    abierta_en = models.DateTimeField(auto_now_add=True)
    cerrada_en = models.DateTimeField(null=True, blank=True)
    saldo_inicial = models.DecimalField(max_digits=14, decimal_places=2)
    saldo_final_declarado = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    saldo_final_sistema = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)


class MovimientoCaja(TimeStampedModel):
    class Tipo(models.TextChoices):
        VENTA = "VENTA", "Venta"
        INGRESO = "INGRESO", "Ingreso"
        GASTO = "GASTO", "Gasto"
        RETIRO = "RETIRO", "Retiro"
        DEVOLUCION = "DEVOLUCION", "Devolución"
    sesion = models.ForeignKey(SesionCaja, on_delete=models.PROTECT, related_name="movimientos")
    tipo = models.CharField(max_length=12, choices=Tipo.choices)
    forma_pago = models.CharField(max_length=20, default="EFECTIVO")
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    referencia = models.CharField(max_length=80, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    observacion = models.TextField(blank=True)
