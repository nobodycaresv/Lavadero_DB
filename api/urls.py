from django.urls import include, path
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD
from .views import EstadoViewSet, MedioPagoViewSet, panel_gestion

router = DefaultRouter()
router.register("estados", EstadoViewSet, basename="estado")
router.register("medios-pago", MedioPagoViewSet, basename="medio-pago")

urlpatterns = [
    path("", include(router.urls)),
    path("panel/", panel_gestion, name="panel-gestion"),
=======

from .views import EstadoAPIView, ServicioViewSet

router = DefaultRouter(trailing_slash=False)
router.register("servicios", ServicioViewSet, basename="servicio")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
>>>>>>> 321c9615e00bfe9f1b5585bc4d4f155548942d22
]