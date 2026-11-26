from rest_framework.routers import SimpleRouter

from .views_insumos import CompraViewSet, InsumoViewSet, MovimientoStockViewSet

# Sin barra final, igual que /api/servicios
router = SimpleRouter(trailing_slash=False)
router.register("insumos", InsumoViewSet, basename="insumo")
router.register("compras", CompraViewSet, basename="compra")
router.register("movimientos", MovimientoStockViewSet, basename="movimiento")

urlpatterns = router.urls