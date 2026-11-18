from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import (
    EstadoAPIView,
    InsumoViewSet,
    ProveedorViewSet,
    ServicioViewSet,
)

router = DefaultRouter()
router.register("proveedores", ProveedorViewSet, basename="proveedor")
router.register("insumos", InsumoViewSet, basename="insumo")
router.register("servicios", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("panel/", TemplateView.as_view(template_name="core/panel.html"), name="panel"),
    path("", include(router.urls)),
]
