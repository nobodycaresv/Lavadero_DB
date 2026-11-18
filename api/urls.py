from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    EstadoViewSet, 
    MedioPagoViewSet, 
    ServicioViewSet, 
    panel_gestion
)

router = DefaultRouter()
router.register("estados", EstadoViewSet, basename="estado")
router.register("medios-pago", MedioPagoViewSet, basename="medio-pago")
router.register("servicios", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("", include(router.urls)),
    path("panel/", panel_gestion, name="panel-gestion"),
]