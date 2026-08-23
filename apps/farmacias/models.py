from django.conf import settings
from django.db import models
from apps.core.models import ActivableModel


class Farmacia(ActivableModel):
    codigo = models.CharField(max_length=30, unique=True)
    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=30, blank=True, db_index=True)
    logo = models.ImageField(upload_to="farmacias/", blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    provincia = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, default="Colombia")
    telefono = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    correo = models.EmailField(blank=True)
    administrador = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="farmacias_administradas")

    def __str__(self): return self.nombre


class UsuarioFarmacia(ActivableModel):
    class Rol(models.TextChoices):
        SUPERADMIN = "SUPERADMIN", "Superadministrador"
        ADMIN = "ADMIN", "Administrador"
        FARMACEUTICO = "FARMACEUTICO", "Farmaceutico"
        INVENTARIO = "INVENTARIO", "Encargado de inventario"
        CAJERO = "CAJERO", "Cajero/Vendedor"
        CONSULTA = "CONSULTA", "Consulta"

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="asignaciones_farmacia")
    farmacia = models.ForeignKey(Farmacia, on_delete=models.PROTECT, related_name="usuarios_asignados")
    rol = models.CharField(max_length=20, choices=Rol.choices)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["usuario", "farmacia"], name="uq_usuario_farmacia")]
        indexes = [models.Index(fields=["farmacia", "activo"])]

