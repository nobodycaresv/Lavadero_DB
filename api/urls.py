from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import EstadoViewSet, MedioPagoViewSet

router = DefaultRouter()
router.register("estados", EstadoViewSet, basename="estado")
router.register("medios-pago", MedioPagoViewSet, basename="medio-pago")

urlpatterns = [
    path("", include(router.urls)),
]