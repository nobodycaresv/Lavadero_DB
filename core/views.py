from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F, Sum
from django.http import Http404
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.utils import timezone

from catalogos.models import Servicio
from finanzas.models import Pago
from insumos.models import Insumo
from operaciones.models import Turno


def home(request):
    servicios = Servicio.objects.filter(activo=True).order_by("-id_servicio")
    return render(request, "core/home.html", {"servicios": servicios})


@staff_member_required(login_url="/admin/login/")
def panel_inicio(request):
    hoy = timezone.localdate()
    contexto = {
        "turnos_hoy": Turno.objects.filter(fecha=hoy).count(),
        "cobrado_hoy": Pago.objects.filter(fecha_hora__date=hoy).aggregate(t=Sum("monto"))["t"] or 0,
        "stock_bajo": Insumo.objects.filter(activo=True, stock_actual__lte=F("stock_minimo")).count(),
    }
    return render(request, "core/panel/inicio.html", contexto)


# Sirve cualquier pantalla del panel: /panel/clientes/ -> core/panel/clientes.html
@staff_member_required(login_url="/admin/login/")
def panel_pagina(request, pagina):
    try:
        return render(request, f"core/panel/{pagina}.html")
    except TemplateDoesNotExist:
        raise Http404
