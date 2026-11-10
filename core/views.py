from django.shortcuts import render
from django.utils import timezone


def home(request):
    return render(request, 'core/home.html', {'hora_actual': timezone.now()})