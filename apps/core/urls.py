from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("medicamentos/", views.medicamentos, name="medicamentos"),
    path("medicamentos/nuevo/", views.medicamento_crear, name="medicamento-crear"),
    path("medicamentos/<int:pk>/editar/", views.medicamento_editar, name="medicamento-editar"),
    path("inventario/", views.inventario, name="inventario"),
    path("inventario/nuevo/", views.inventario_crear, name="inventario-crear"),
    path("inventario/<int:pk>/editar/", views.inventario_editar, name="inventario-editar"),
    path("lotes/", views.lotes, name="lotes"),
    path("lotes/nuevo/", views.lote_crear, name="lote-crear"),
    path("lotes/<int:pk>/editar/", views.lote_editar, name="lote-editar"),
    path("farmacia/<int:pk>/activar/", views.cambiar_farmacia, name="cambiar-farmacia"),
]
