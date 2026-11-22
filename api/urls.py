from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EstadoAPIView, ServicioViewSet
from .views_empresas_facturas import (
    ClienteOpcionesViewSet,
    ConvenioViewSet,
    EmpresaViewSet,
    FacturaViewSet,
    OrdenOpcionesViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("servicios", ServicioViewSet, basename="servicio")
router.register("empresas", EmpresaViewSet, basename="empresa")
router.register("convenios", ConvenioViewSet, basename="convenio")
router.register("facturas", FacturaViewSet, basename="factura")
router.register("facturas-clientes", ClienteOpcionesViewSet, basename="factura-cliente")
router.register("facturas-ordenes", OrdenOpcionesViewSet, basename="factura-orden")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
]
