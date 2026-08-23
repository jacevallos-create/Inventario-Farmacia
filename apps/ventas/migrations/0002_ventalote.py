import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("lotes", "0001_initial"), ("ventas", "0001_initial")]
    operations = [migrations.CreateModel(
        name="VentaLote",
        fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("creado_en", models.DateTimeField(auto_now_add=True)), ("actualizado_en", models.DateTimeField(auto_now=True)),
            ("cantidad", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ("precio_unitario", models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(0)])),
            ("lote", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="detalles_venta", to="lotes.lote")),
            ("venta", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lotes_consumidos", to="ventas.venta")),
        ],
        options={"constraints": [models.UniqueConstraint(fields=("venta", "lote"), name="uq_venta_lote")]},
    )]
