from django.shortcuts import render

from catalogos.models import Servicio


def home(request):
    servicios = Servicio.objects.filter(activo=True).order_by("-id_servicio")
    return render(request, "core/home.html", {"servicios": servicios})


def crud_servicios(request):
    return render(request, "core/servicios_crud.html")
