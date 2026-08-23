from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel


class Transferencia(TimeStampedModel):
    class Estado(models.TextChoices):
        SOLICITADA = "SOLICITADA", "Solicitada"
        APROBADA = "APROBADA", "Aprobada"
        TRANSITO = "TRANSITO", "En tránsito"
        RECIBIDA = "RECIBIDA", "Recibida"
        RECHAZADA = "RECHAZADA", "Rechazada"
    origen = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="transferencias_salida")
    destino = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="transferencias_entrada")
    numero = models.CharField(max_length=40, unique=True)
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.SOLICITADA)
    solicitado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="transferencias_solicitadas")
    aprobado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.PROTECT, related_name="transferencias_aprobadas")
    observacion = models.TextField(blank=True)


class TransferenciaDetalle(TimeStampedModel):
    transferencia = models.ForeignKey(Transferencia, on_delete=models.CASCADE, related_name="detalles")
    medicamento = models.ForeignKey("medicamentos.Medicamento", on_delete=models.PROTECT)
    lote = models.ForeignKey("lotes.Lote", on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
