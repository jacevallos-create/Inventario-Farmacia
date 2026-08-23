from django.db import models
from apps.core.models import ActivableModel


class Medicamento(ActivableModel):
    codigo_interno = models.CharField(max_length=50, unique=True)
    codigo_barras = models.CharField(max_length=64, unique=True, null=True, blank=True)
    nombre_comercial = models.CharField(max_length=180, db_index=True)
    principio_activo = models.CharField(max_length=180, blank=True, db_index=True)
    concentracion = models.CharField(max_length=80, blank=True)
    forma_farmaceutica = models.CharField(max_length=100, blank=True)
    presentacion = models.CharField(max_length=120, blank=True)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey("categorias.Categoria", on_delete=models.PROTECT, related_name="medicamentos")
    laboratorio = models.ForeignKey("laboratorios.Laboratorio", on_delete=models.PROTECT, related_name="medicamentos")
    imagen = models.ImageField(upload_to="medicamentos/", blank=True)
    requiere_receta = models.BooleanField(default=False)
    temperatura_almacenamiento = models.CharField(max_length=100, blank=True)
    observaciones = models.TextField(blank=True)
    def __str__(self): return self.nombre_comercial

