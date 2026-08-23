from django.db import models
from apps.core.models import TimeStampedModel


class ConfiguracionFarmacia(TimeStampedModel):
    farmacia = models.OneToOneField("farmacias.Farmacia", on_delete=models.CASCADE, related_name="configuracion")
    ruc = models.CharField(max_length=13, blank=True)
    razon_social = models.CharField(max_length=180, blank=True)
    nombre_comercial = models.CharField(max_length=180, blank=True)
    establecimiento = models.CharField(max_length=3, default="001")
    punto_emision = models.CharField(max_length=3, default="001")
    direccion_matriz = models.CharField(max_length=255, blank=True)
    obligado_contabilidad = models.BooleanField(default=False)
    ambiente_sri = models.CharField(max_length=10, choices=[("PRUEBAS", "Pruebas"), ("PRODUCCION", "Producción")], default="PRODUCCION")
    certificado_cifrado = models.BinaryField(null=True, blank=True)
    clave_certificado_cifrada = models.BinaryField(null=True, blank=True)
    certificado_nombre = models.CharField(max_length=180, blank=True)
    certificado_expira = models.DateTimeField(null=True, blank=True)
    facturacion_activa = models.BooleanField(default=False)
    alertas_vencimiento_dias = models.PositiveIntegerField(default=90)

    @property
    def lista_para_facturar(self):
        return bool(self.facturacion_activa and self.ruc and self.certificado_cifrado and self.certificado_expira)
