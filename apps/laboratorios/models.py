from django.db import models
from apps.core.models import ActivableModel


class Laboratorio(ActivableModel):
    nombre = models.CharField(max_length=150, unique=True)
    ruc = models.CharField(max_length=30, blank=True)
    pais = models.CharField(max_length=100, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    contacto = models.CharField(max_length=120, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    sitio_web = models.URLField(blank=True)
    def __str__(self): return self.nombre

