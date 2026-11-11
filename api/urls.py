from django.urls import include, path
from rest_framework.routers import DefaultRouter
 
from .views import EstadoAPIView, ProveedorViewSet, InsumoViewSet
 
router = DefaultRouter()
router.register("proveedores", ProveedorViewSet, basename="proveedor")
router.register("insumos", InsumoViewSet, basename="insumo")
 
urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
]
