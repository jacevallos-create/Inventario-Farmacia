import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("farmacias", "0002_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(
        name="AuditLog",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("creado_en", models.DateTimeField(auto_now_add=True)), ("actualizado_en", models.DateTimeField(auto_now=True)),
            ("accion", models.CharField(choices=[("CREAR", "Crear"), ("MODIFICAR", "Modificar"), ("ELIMINAR", "Eliminar")], max_length=12)),
            ("entidad", models.CharField(db_index=True, max_length=40)), ("objeto_id", models.CharField(max_length=80)),
            ("descripcion", models.CharField(max_length=255)), ("cambios", models.JSONField(blank=True, default=dict)),
            ("ip", models.GenericIPAddressField(blank=True, null=True)),
            ("farmacia", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="auditorias", to="farmacias.farmacia")),
            ("usuario", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="auditorias", to=settings.AUTH_USER_MODEL)),
        ],
        options={"ordering": ["-creado_en"], "indexes": [models.Index(fields=["entidad", "creado_en"], name="auditoria_a_entidad_0d2b1d_idx"), models.Index(fields=["farmacia", "creado_en"], name="auditoria_a_farmaci_a54a22_idx")]},
    )]
