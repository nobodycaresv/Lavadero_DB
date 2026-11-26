from rest_framework.routers import SimpleRouter

from .views_clientes import ClienteViewSet, VehiculoViewSet

# Sin barra final, igual que /api/servicios
router = SimpleRouter(trailing_slash=False)
router.register("clientes", ClienteViewSet, basename="cliente")
router.register("vehiculos", VehiculoViewSet, basename="vehiculo")

urlpatterns = router.urls