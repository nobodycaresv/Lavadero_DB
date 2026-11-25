from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .operaciones_views import DetalleServicioViewSet, FichaTecnicaViewSet, OrdenTrabajoViewSet
from .views import EmpleadoViewSet, EstadoAPIView, ServicioViewSet

router = DefaultRouter(trailing_slash=False)
router.register("servicios", ServicioViewSet, basename="servicio")
router.register("empleados", EmpleadoViewSet, basename="empleado")
router.register("fichas", FichaTecnicaViewSet, basename="ficha")
router.register("ordenes", OrdenTrabajoViewSet, basename="orden")
router.register("detalles-servicio", DetalleServicioViewSet, basename="detalle-servicio")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
]