from django.contrib import admin
from .models import HistorialPrecio, InventarioFarmacia, MovimientoInventario
admin.site.register(InventarioFarmacia)
admin.site.register(MovimientoInventario)
admin.site.register(HistorialPrecio)
