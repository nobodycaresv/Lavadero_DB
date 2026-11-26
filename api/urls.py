from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .operaciones_views import DetalleServicioViewSet, FichaTecnicaViewSet, OrdenTrabajoViewSet
from .turno_views import TurnoViewSet
from .views import (
    EmpleadoViewSet,
    EstadoAPIView,
    EstadoViewSet,
    MedioPagoViewSet,
    PagoViewSet,
    ServicioViewSet,
)
from .views_empresas_facturas import (
    ClienteOpcionesViewSet,
    ConvenioViewSet,
    EmpresaViewSet,
    FacturaViewSet,
    OrdenOpcionesViewSet,
)

router = DefaultRouter(trailing_slash=False)
router.register("servicios", ServicioViewSet, basename="servicio")
router.register("turnos", TurnoViewSet, basename="turno")
router.register("empleados", EmpleadoViewSet, basename="empleado")
router.register("fichas", FichaTecnicaViewSet, basename="ficha")
router.register("ordenes", OrdenTrabajoViewSet, basename="orden")
router.register("detalles-servicio", DetalleServicioViewSet, basename="detalle-servicio")
router.register("estados", EstadoViewSet, basename="estado")
router.register("medios-pago", MedioPagoViewSet, basename="medio-pago")
router.register("pagos", PagoViewSet, basename="pago")
router.register("empresas", EmpresaViewSet, basename="empresa")
router.register("convenios", ConvenioViewSet, basename="convenio")
router.register("facturas", FacturaViewSet, basename="factura")
router.register("facturas-clientes", ClienteOpcionesViewSet, basename="factura-cliente")
router.register("facturas-ordenes", OrdenOpcionesViewSet, basename="factura-orden")

urlpatterns = [
    path("estado/", EstadoAPIView.as_view(), name="api-estado"),
    path("", include(router.urls)),
    path("", include("api.rutas_clientes")),
    path("", include("api.rutas_insumos")),
]
