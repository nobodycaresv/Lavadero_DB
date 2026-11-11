from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ConvenioViewSet, EmpresaViewSet, EstadoAPIView, ServicioViewSet

router = DefaultRouter(trailing_slash=False)
router.register("servicios", ServicioViewSet, basename="servicio")
router.register("empresas", EmpresaViewSet, basename="empresa")
router.register("convenios", ConvenioViewSet, basename="convenio")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
]