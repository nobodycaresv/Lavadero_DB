from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from .views import ClienteViewSet, EstadoAPIView, VehiculoViewSet

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("vehiculos", VehiculoViewSet, basename="vehiculo")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("panel/", TemplateView.as_view(template_name="api/panel.html"), name="panel"),
    path("", include(router.urls)),
]