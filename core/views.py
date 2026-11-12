from django.shortcuts import render
from django.utils import timezone


def home(request):
    contexto = {
        'hora_actual': timezone.now(),
    }
    return render(request, 'core/home.html', contexto)

def panel_empresas_convenios(request):
    return render(request, 'panel_empresas_convenios.html')
