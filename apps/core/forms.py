from django import forms

from apps.inventario.models import InventarioFarmacia
from apps.lotes.models import Lote
from apps.medicamentos.models import Medicamento


class StyledModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class MedicamentoForm(StyledModelForm):
    class Meta:
        model = Medicamento
        fields = ["codigo_interno", "codigo_barras", "nombre_comercial", "principio_activo", "concentracion", "forma_farmaceutica", "presentacion", "categoria", "laboratorio", "requiere_receta", "temperatura_almacenamiento", "descripcion", "observaciones", "activo"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 3}), "observaciones": forms.Textarea(attrs={"rows": 3})}


class InventarioForm(StyledModelForm):
    class Meta:
        model = InventarioFarmacia
        fields = ["medicamento", "stock_actual", "stock_minimo", "stock_maximo", "ubicacion", "precio_venta"]

    def __init__(self, *args, farmacia=None, **kwargs):
        self.farmacia = farmacia
        super().__init__(*args, **kwargs)
        if farmacia:
            usados = InventarioFarmacia.objects.filter(farmacia=farmacia).exclude(pk=self.instance.pk).values_list("medicamento_id", flat=True)
            self.fields["medicamento"].queryset = Medicamento.objects.filter(activo=True).exclude(pk__in=usados)

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.farmacia = self.farmacia
        if commit:
            instance.save()
        return instance


class LoteForm(StyledModelForm):
    class Meta:
        model = Lote
        fields = ["medicamento", "proveedor", "numero", "fecha_fabricacion", "fecha_vencimiento", "cantidad_inicial", "cantidad_disponible", "costo_unitario"]
        widgets = {"fecha_fabricacion": forms.DateInput(attrs={"type": "date"}), "fecha_vencimiento": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, farmacia=None, **kwargs):
        self.farmacia = farmacia
        super().__init__(*args, **kwargs)
        if farmacia:
            ids = InventarioFarmacia.objects.filter(farmacia=farmacia).values_list("medicamento_id", flat=True)
            self.fields["medicamento"].queryset = Medicamento.objects.filter(pk__in=ids, activo=True)

    def clean(self):
        data = super().clean()
        if data.get("cantidad_disponible", 0) > data.get("cantidad_inicial", 0):
            self.add_error("cantidad_disponible", "No puede superar la cantidad inicial.")
        return data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.farmacia = self.farmacia
        if commit:
            instance.save()
        return instance
