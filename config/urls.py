from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", core_views.home, name="home"),

    # Link viejo del home: ahora redirige al panel
    path("servicios/", RedirectView.as_view(url="/panel/servicios/"), name="crud_servicios"),

    # Panel de gestión (cada pantalla nueva suma UNA línea acá)
    path("panel/", core_views.panel_inicio, name="panel_inicio"),
    path("panel/servicios/", core_views.panel_servicios, name="panel_servicios"),
]
