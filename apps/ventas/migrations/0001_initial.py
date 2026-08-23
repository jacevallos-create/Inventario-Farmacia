import django.core.validators
import django.db.models.deletion
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("farmacias", "0002_initial"),
        ("medicamentos", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="Venta",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("referencia_cliente", models.CharField(max_length=64, unique=True)),
                ("cliente_nombre", models.CharField(default="Consumidor final", max_length=180)),
                ("cantidad", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("precio_unitario", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0"))])),
                ("total", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0"))])),
                ("farmacia", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ventas", to="farmacias.farmacia")),
                ("medicamento", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ventas", to="medicamentos.medicamento")),
                ("usuario", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ventas", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-creado_en"], "indexes": [models.Index(fields=["farmacia", "creado_en"], name="ventas_vent_farmaci_11617d_idx")]},
        )
    ]
