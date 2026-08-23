from django.db import models
from apps.core.models import ActivableModel


class Proveedor(ActivableModel):
    ruc = models.CharField(max_length=30, unique=True)
    razon_social = models.CharField(max_length=180)
    nombre_comercial = models.CharField(max_length=180, blank=True)
    contacto = models.CharField(max_length=120, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    tipo = models.CharField(max_length=80, blank=True)
    def __str__(self): return self.nombre_comercial or self.razon_social

