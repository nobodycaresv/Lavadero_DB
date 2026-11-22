from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", core_views.home, name="home"),

    # Link viejo del home: redirige al panel
    path("servicios/", RedirectView.as_view(url="/panel/servicios/"), name="crud_servicios"),

    # Panel: /panel/ es el inicio; /panel/<nombre>/ muestra core/panel/<nombre>.html
    path("panel/", core_views.panel_inicio, name="panel_inicio"),
    path("panel/<slug:pagina>/", core_views.panel_pagina, name="panel_pagina"),
]
