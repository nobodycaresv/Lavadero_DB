from django.contrib.auth.decorators import login_required
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter, SimpleRouter

from .views import ClienteViewSet, EstadoAPIView, ServicioViewSet, VehiculoViewSet

# Clientes y vehículos (panel.js): rutas CON barra final -> /api/clientes/
router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("vehiculos", VehiculoViewSet, basename="vehiculo")

# Servicios (home.html): rutas SIN barra final -> /api/servicios
router_servicios = SimpleRouter(trailing_slash=False)
router_servicios.register("servicios", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("panel/", login_required(TemplateView.as_view(template_name="api/panel.html")), name="panel"),
    path("", include(router_servicios.urls)),
    path("", include(router.urls)),
]