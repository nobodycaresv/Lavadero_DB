from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from catalogos.models import Estado, MedioPago, Servicio
from finanzas.models import Pago

from .serializers import (
    EstadoSerializer,
    MedioPagoSerializer,
    PagoSerializer,
    ServicioSerializer,
)


class EstadoAPIView(APIView):
    """Endpoint de ejemplo para confirmar que la API REST esta funcionando correctamente."""

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
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Servicio.objects.all().order_by("id_servicio")
    serializer_class = ServicioSerializer

    @action(detail=True, methods=["patch"])
    def desactivar(self, request, pk=None):
        servicio = self.get_object()
        servicio.activo = False
        servicio.save(update_fields=["activo"])
        return Response(self.get_serializer(servicio).data)