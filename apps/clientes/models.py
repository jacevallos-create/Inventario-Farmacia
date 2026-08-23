from django.db import models
from apps.core.models import ActivableModel


class Cliente(ActivableModel):
    farmacia = models.ForeignKey("farmacias.Farmacia", on_delete=models.PROTECT, related_name="clientes")
    identificacion = models.CharField(max_length=30)
    nombres = models.CharField(max_length=120)
    apellidos = models.CharField(max_length=120, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["farmacia", "identificacion"], name="uq_cliente_identificacion_farmacia")]

