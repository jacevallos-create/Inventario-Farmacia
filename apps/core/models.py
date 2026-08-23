from django.db import models


class TimeStampedModel(models.Model):
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class ActivableModel(TimeStampedModel):
    activo = models.BooleanField(default=True, db_index=True)

    class Meta:
        abstract = True
