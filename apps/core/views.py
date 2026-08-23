from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import F, Q, Sum
from django.conf import settings
from django.http import FileResponse, Http404
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.farmacias.models import Farmacia, UsuarioFarmacia
from apps.inventario.models import InventarioFarmacia, MovimientoInventario
from apps.lotes.models import Lote
from apps.medicamentos.models import Medicamento
from .forms import InventarioForm, LoteForm, MedicamentoForm


def _farmacia_activa(request):
    farmacia_id = request.session.get("farmacia_id")
    permitidas = Farmacia.objects.filter(usuarios_asignados__usuario=request.user, usuarios_asignados__activo=True, activo=True)
    if request.user.is_superuser:
        permitidas = Farmacia.objects.filter(activo=True)
    farmacia = permitidas.filter(pk=farmacia_id).first() if farmacia_id else permitidas.first()
    if farmacia:
        request.session["farmacia_id"] = farmacia.pk
    return farmacia


def landing(request):
    index = settings.BASE_DIR / "static" / "frontend" / "index.html"
    if not index.exists():
        raise Http404("Frontend no compilado. Ejecute npm.cmd run build dentro de frontend.")
    return FileResponse(index.open("rb"), content_type="text/html; charset=utf-8")


@login_required
def dashboard(request):
    farmacia = _farmacia_activa(request)
    inventarios = InventarioFarmacia.objects.none()
    lotes = Lote.objects.none()
    movimientos = MovimientoInventario.objects.none()
    if farmacia:
        inventarios = InventarioFarmacia.objects.filter(farmacia=farmacia).select_related("medicamento", "medicamento__categoria")
        lotes = Lote.objects.filter(farmacia=farmacia).select_related("medicamento")
        movimientos = MovimientoInventario.objects.filter(farmacia=farmacia).select_related("medicamento", "usuario")[:8]
    hoy = timezone.localdate()
    context = {
        "farmacia": farmacia,
        "productos": inventarios.count(),
        "unidades": inventarios.aggregate(total=Sum("stock_actual"))["total"] or 0,
        "stock_bajo": inventarios.filter(stock_actual__lte=F("stock_minimo"), stock_actual__gt=0).count(),
        "agotados": inventarios.filter(stock_actual=0).count(),
        "proximos_vencer": lotes.filter(fecha_vencimiento__range=(hoy, hoy + timedelta(days=60)), cantidad_disponible__gt=0).count(),
        "vencidos": lotes.filter(fecha_vencimiento__lt=hoy, cantidad_disponible__gt=0).count(),
        "inventarios_criticos": inventarios.filter(stock_actual__lte=F("stock_minimo")).order_by("stock_actual")[:6],
        "lotes_proximos": lotes.filter(fecha_vencimiento__lte=hoy + timedelta(days=90), cantidad_disponible__gt=0).order_by("fecha_vencimiento")[:6],
        "movimientos": movimientos,
    }
    return render(request, "dashboard/index.html", context)


def _listado(request, queryset, template, titulo):
    q = request.GET.get("q", "").strip()
    if q:
        queryset = queryset.filter(Q(medicamento__nombre_comercial__icontains=q) | Q(medicamento__codigo_interno__icontains=q) | Q(medicamento__codigo_barras__icontains=q))
    pagina = Paginator(queryset, 20).get_page(request.GET.get("page"))
    return render(request, template, {"pagina": pagina, "titulo": titulo, "q": q, "farmacia": _farmacia_activa(request)})


@login_required
def inventario(request):
    farmacia = _farmacia_activa(request)
    qs = InventarioFarmacia.objects.filter(farmacia=farmacia).select_related("medicamento", "medicamento__categoria", "medicamento__laboratorio") if farmacia else InventarioFarmacia.objects.none()
    return _listado(request, qs.order_by("medicamento__nombre_comercial"), "inventario/lista.html", "Inventario")


@login_required
def medicamentos(request):
    farmacia = _farmacia_activa(request)
    qs = InventarioFarmacia.objects.filter(farmacia=farmacia).select_related("medicamento", "medicamento__categoria", "medicamento__laboratorio") if farmacia else InventarioFarmacia.objects.none()
    return _listado(request, qs.order_by("medicamento__nombre_comercial"), "medicamentos/lista.html", "Medicamentos")


@login_required
def lotes(request):
    farmacia = _farmacia_activa(request)
    qs = Lote.objects.filter(farmacia=farmacia).select_related("medicamento", "proveedor") if farmacia else Lote.objects.none()
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(medicamento__nombre_comercial__icontains=q) | Q(numero__icontains=q))
    return render(request, "lotes/lista.html", {"pagina": Paginator(qs.order_by("fecha_vencimiento"), 20).get_page(request.GET.get("page")), "q": q, "farmacia": farmacia, "hoy": timezone.localdate()})


def _formulario(request, form_class, titulo, volver, instance=None, farmacia=None):
    kwargs = {"instance": instance}
    if form_class in (InventarioForm, LoteForm):
        kwargs["farmacia"] = farmacia
    form = form_class(request.POST or None, request.FILES or None, **kwargs)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Los cambios se guardaron correctamente.")
        return redirect(volver)
    return render(request, "includes/model_form.html", {"form": form, "titulo": titulo, "volver": volver, "farmacia": farmacia})


@login_required
def medicamento_crear(request):
    return _formulario(request, MedicamentoForm, "Registrar medicamento", "medicamentos", farmacia=_farmacia_activa(request))


@login_required
def medicamento_editar(request, pk):
    farmacia = _farmacia_activa(request)
    permitido = InventarioFarmacia.objects.filter(farmacia=farmacia, medicamento_id=pk).exists() or request.user.is_superuser
    if not permitido:
        raise Http404
    return _formulario(request, MedicamentoForm, "Editar medicamento", "medicamentos", get_object_or_404(Medicamento, pk=pk), farmacia)


@login_required
def inventario_crear(request):
    return _formulario(request, InventarioForm, "Agregar al inventario", "inventario", farmacia=_farmacia_activa(request))


@login_required
def inventario_editar(request, pk):
    farmacia = _farmacia_activa(request)
    item = get_object_or_404(InventarioFarmacia, pk=pk, farmacia=farmacia)
    return _formulario(request, InventarioForm, "Editar inventario", "inventario", item, farmacia)


@login_required
def lote_crear(request):
    return _formulario(request, LoteForm, "Registrar lote", "lotes", farmacia=_farmacia_activa(request))


@login_required
def lote_editar(request, pk):
    farmacia = _farmacia_activa(request)
    lote = get_object_or_404(Lote, pk=pk, farmacia=farmacia)
    return _formulario(request, LoteForm, "Editar lote", "lotes", lote, farmacia)


@login_required
def cambiar_farmacia(request, pk):
    permitida = UsuarioFarmacia.objects.filter(usuario=request.user, farmacia_id=pk, activo=True).exists()
    if not (permitida or request.user.is_superuser):
        raise Http404
    request.session["farmacia_id"] = pk
    return dashboard(request)
