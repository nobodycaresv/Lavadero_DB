from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EstadoAPIView, ServicioViewSet

router = DefaultRouter(trailing_slash=False)
router.register("servicios", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
]