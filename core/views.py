from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.models import F, Sum
from django.http import Http404
from django.shortcuts import redirect, render
from django.template import TemplateDoesNotExist
from django.utils import timezone

from catalogos.models import Servicio
from finanzas.models import Pago
from insumos.models import Insumo
from operaciones.models import Turno


def home(request):
    servicios = Servicio.objects.filter(activo=True).order_by("-id_servicio")
    return render(request, "core/home.html", {"servicios": servicios})


@staff_member_required(login_url="login")
def panel_inicio(request):
    hoy = timezone.localdate()
    contexto = {
        "turnos_hoy": Turno.objects.filter(fecha=hoy).count(),
        "cobrado_hoy": Pago.objects.filter(fecha_hora__date=hoy).aggregate(t=Sum("monto"))["t"] or 0,
        "stock_bajo": Insumo.objects.filter(activo=True, stock_actual__lte=F("stock_minimo")).count(),
    }
    return render(request, "core/panel/inicio.html", contexto)


# Sirve cualquier pantalla del panel: /panel/clientes/ -> core/panel/clientes.html
@staff_member_required(login_url="login")
def panel_pagina(request, pagina):
    try:
        return render(request, f"core/panel/{pagina}.html")
    except TemplateDoesNotExist:
        raise Http404


def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("panel_inicio")

    error = None
    if request.method == "POST":
        dato = request.POST.get("correo", "").strip()
        clave = request.POST.get("contrasena", "")
        # Se puede entrar con el correo o con el nombre de usuario
        usuario = get_user_model().objects.filter(email__iexact=dato).first()
        user = authenticate(request, username=usuario.get_username() if usuario else dato, password=clave)
        if user is None:
            error = "Correo o contraseña incorrectos."
        elif not user.is_staff:
            error = "Tu usuario no tiene permiso para entrar al panel."
        else:
            login(request, user)
            return redirect(request.GET.get("next") or "panel_inicio")

    return render(request, "core/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")
