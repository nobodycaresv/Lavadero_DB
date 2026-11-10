from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, EstadoAPIView, VehiculoViewSet

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("vehiculos", VehiculoViewSet, basename="vehiculo")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
]