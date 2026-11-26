from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogos.models import Empleado, Estado, MedioPago, Servicio
from finanzas.models import Pago

from .permissions import LecturaPublicaEscrituraStaff
from .serializers import (
    EmpleadoSerializer,
    EstadoSerializer,
    MedioPagoSerializer,
    PagoSerializer,
    ServicioSerializer,
)


class EstadoAPIView(APIView):
    """Endpoint de ejemplo para confirmar que la API REST esta funcionando correctamente."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            {
                "estado": "ok",
                "mensaje": "La API REST del proyecto esta funcionando correctamente.",
            },
            status=status.HTTP_200_OK,
        )


class EstadoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Estado.objects.all().order_by("id_estado")
    serializer_class = EstadoSerializer


class MedioPagoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = MedioPago.objects.all().order_by("id_medio_pago")
    serializer_class = MedioPagoSerializer


class PagoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Pago.objects.all().order_by("-id_pago")
    serializer_class = PagoSerializer


class ServicioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Servicio.objects.all().order_by("id_servicio")
    serializer_class = ServicioSerializer
    permission_classes = [LecturaPublicaEscrituraStaff]

    def get_queryset(self):
        # El público solo ve los servicios activos; el personal ve todos
        if self.request.user.is_staff:
            return self.queryset
        return self.queryset.filter(activo=True)

    @action(detail=True, methods=["patch"])
    def desactivar(self, request, pk=None):
        servicio = self.get_object()
        servicio.activo = False
        servicio.save(update_fields=["activo"])
        return Response(self.get_serializer(servicio).data)


class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    Catálogo de empleados (permite filtrar opcionalmente por rol).
    """

    serializer_class = EmpleadoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "apellido", "rol"]

    def get_queryset(self):
        qs = Empleado.objects.order_by("nombre", "apellido")
        rol = self.request.query_params.get("rol")
        if rol:
            qs = qs.filter(rol__iexact=rol)
        return qs