import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("inventario", "0002_initial")]
    operations = [
        migrations.AddField(
            model_name="inventariofarmacia",
            name="precio_compra",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal("0"))]),
        )
    ]
