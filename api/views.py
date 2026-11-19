from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from clientes.models import Cliente, Vehiculo

from .serializers import ClienteSerializer, ServicioSerializer, VehiculoSerializer


class EstadoAPIView(APIView):
    """Endpoint de ejemplo para confirmar que la API REST esta funcionando."""

    def get(self, request):
        return Response(
            {"estado": "ok", "mensaje": "La API REST del proyecto esta funcionando correctamente."},
            status=status.HTTP_200_OK,
        )


class BajaLogicaViewSet(viewsets.ModelViewSet):
    """CRUD base con baja lógica (activo=False)."""

    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        # si no viene ?activo=false, devuelve solo los activos
        activo = self.request.query_params.get("activo", "true").lower() != "false"
        return self.queryset.filter(activo=activo)

    def perform_destroy(self, instance):
        # el DELETE solo marca como inactivo, no borra de la base
        instance.activo = False
        instance.save(update_fields=["activo"])


class ClienteViewSet(BajaLogicaViewSet):
    queryset = Cliente.objects.prefetch_related("vehiculos").order_by("apellido", "nombre")
    serializer_class = ClienteSerializer
    search_fields = ["nombre", "apellido", "telefono", "email"]


class VehiculoViewSet(BajaLogicaViewSet):
    queryset = Vehiculo.objects.select_related("cliente").order_by("patente")
    serializer_class = VehiculoSerializer
    search_fields = ["patente", "marca", "modelo"]

    def get_queryset(self):
        qs = super().get_queryset()
        cliente = self.request.query_params.get("cliente")  # ej: /api/vehiculos/?cliente=3
        return qs.filter(cliente_id=cliente) if cliente else qs
