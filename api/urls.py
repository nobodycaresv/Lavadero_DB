from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EmpleadoViewSet, panel_gestion

router = DefaultRouter()
router.register("empleados", EmpleadoViewSet, basename="empleado")

urlpatterns = [
    path("", include(router.urls)),
    path("panel/", panel_gestion, name="panel-gestion"),
]   