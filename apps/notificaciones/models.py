from django.conf import settings
from django.db import models
from apps.core.models import TimeStampedModel


class Notificacion(TimeStampedModel):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notificaciones")
    farmacia = models.ForeignKey("farmacias.Farmacia", null=True, blank=True, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=30)
    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    leida = models.BooleanField(default=False, db_index=True)
    enlace = models.CharField(max_length=255, blank=True)
