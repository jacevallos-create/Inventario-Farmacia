from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.categorias.models import Categoria
from apps.farmacias.models import Farmacia, UsuarioFarmacia
from apps.inventario.models import InventarioFarmacia
from apps.laboratorios.models import Laboratorio
from apps.lotes.models import Lote
from apps.medicamentos.models import Medicamento
from apps.proveedores.models import Proveedor
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crea datos demostrativos idempotentes para desarrollo."

    @transaction.atomic
    def handle(self, *args, **options):
        usuario, creado = Usuario.objects.get_or_create(
            email="admin@demo.local",
            defaults={"first_name": "Administrador", "is_staff": True, "is_superuser": True},
        )
        if creado:
            usuario.set_password("AdminDemo2026!")
            usuario.save(update_fields=["password"])

        farmacia, _ = Farmacia.objects.get_or_create(
            codigo="FAR-001",
            defaults={"nombre": "Farmacia Demo", "ruc": "900000001", "ciudad": "Bogota", "administrador": usuario},
        )
        UsuarioFarmacia.objects.get_or_create(
            usuario=usuario, farmacia=farmacia,
            defaults={"rol": UsuarioFarmacia.Rol.SUPERADMIN},
        )
        categoria, _ = Categoria.objects.get_or_create(nombre="Analgesicos", defaults={"descripcion": "Dolor y fiebre"})
        laboratorio, _ = Laboratorio.objects.get_or_create(nombre="Laboratorio Demo", defaults={"pais": "Colombia"})
        proveedor, _ = Proveedor.objects.get_or_create(
            ruc="900000002", defaults={"razon_social": "Distribuidora Demo SAS", "nombre_comercial": "Distribuidora Demo"}
        )
        medicamento, _ = Medicamento.objects.get_or_create(
            codigo_interno="MED-001",
            defaults={
                "codigo_barras": "770000000001", "nombre_comercial": "Acetaminofen 500 mg",
                "principio_activo": "Paracetamol", "concentracion": "500 mg", "forma_farmaceutica": "Tableta",
                "presentacion": "Caja x 20", "categoria": categoria, "laboratorio": laboratorio,
            },
        )
        InventarioFarmacia.objects.get_or_create(
            farmacia=farmacia, medicamento=medicamento,
            defaults={"stock_actual": 100, "stock_minimo": 20, "stock_maximo": 300, "ubicacion": "A-01", "precio_venta": Decimal("8.50")},
        )
        Lote.objects.get_or_create(
            farmacia=farmacia, medicamento=medicamento, numero="LOTE-DEMO-01",
            defaults={"proveedor": proveedor, "fecha_vencimiento": date.today() + timedelta(days=365), "cantidad_inicial": 100, "cantidad_disponible": 100, "costo_unitario": Decimal("5.00")},
        )
        self.stdout.write(self.style.SUCCESS("Datos demo listos. Usuario: admin@demo.local / AdminDemo2026!"))
