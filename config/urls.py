from django.contrib import admin
from django.urls import include, path
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path("", core_views.home, name="home"),
    path("servicios/", core_views.crud_servicios, name="crud_servicios"),
]
