from django.conf import settings
from django.db import models

from apps.core.models import TimeStampedModel


class AuditLog(TimeStampedModel):
    class Accion(models.TextChoices):
        CREAR = "CREAR", "Crear"
        MODIFICAR = "MODIFICAR", "Modificar"
        ELIMINAR = "ELIMINAR", "Eliminar"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name="auditorias")
    farmacia = models.ForeignKey("farmacias.Farmacia", null=True, blank=True, on_delete=models.SET_NULL, related_name="auditorias")
    accion = models.CharField(max_length=12, choices=Accion.choices)
    entidad = models.CharField(max_length=40, db_index=True)
    objeto_id = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=255)
    cambios = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-creado_en"]
        indexes = [models.Index(fields=["entidad", "creado_en"]), models.Index(fields=["farmacia", "creado_en"])]
