from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, render
from django.utils import timezone


def home(request):
    return render(request, 'core/home.html', {'hora_actual': timezone.now()})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('panel')

    error = None
    if request.method == 'POST':
        correo = request.POST.get('correo', '').strip()
        clave = request.POST.get('contrasena', '')
        # Django autentica por username: buscamos el usuario por su correo
        usuario = get_user_model().objects.filter(email__iexact=correo).first()
        user = authenticate(request, username=usuario.get_username(), password=clave) if usuario else None
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next') or 'panel')
        error = 'Correo o contraseña incorrectos.'

    return render(request, 'core/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')