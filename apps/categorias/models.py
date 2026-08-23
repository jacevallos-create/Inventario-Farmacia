from django.db import models
from apps.core.models import ActivableModel


class Categoria(ActivableModel):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=60, blank=True)
    def __str__(self): return self.nombre

