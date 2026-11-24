from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EstadoAPIView,
    EstadoViewSet,
    MedioPagoViewSet,
    PagoViewSet,
    ServicioViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("estados", EstadoViewSet, basename="estado")
router.register("medios-pago", MedioPagoViewSet, basename="medio-pago")
router.register("pagos", PagoViewSet, basename="pago")
router.register("servicios", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
]