from django.urls import include, path
from rest_framework.routers import DefaultRouter
from django.views.generic import TemplateView
from .views import EstadoAPIView, ProveedorViewSet, InsumoViewSet
 
router = DefaultRouter()
router.register("proveedores", ProveedorViewSet, basename="proveedor")
router.register("insumos", InsumoViewSet, basename="insumo")
 
urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("panel/", TemplateView.as_view(template_name="core/panel.html"), name="panel"),
    path("", include(router.urls)),
]
