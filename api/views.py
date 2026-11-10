from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Cliente, Vehiculo

from .serializers import ClienteSerializer, VehiculoSerializer

class EstadoAPIView(APIView):
    """Endpoint de prueba: http://localhost:8000/api/estado/"""

    def get(self, request):
        return Response(
            {"estado": "ok", "mensaje": "La API REST del proyecto esta funcionando correctamente."},
            status=status.HTTP_200_OK,
        )

class SoftDeleteMixin:
    """
    Los modelos usan on_delete=PROTECT, así que borrar un cliente con vehículos
    o turnos lanzaría ProtectedError. En vez de eso hacemos baja lógica (activo=False).
    """

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])


class ClienteViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "apellido", "telefono", "email"]

    def get_queryset(self):
        qs = Cliente.objects.prefetch_related("vehiculos").order_by("apellido", "nombre")
        # Por defecto solo activos; ?activo=false para ver los dados de baja
        activo = self.request.query_params.get("activo", "true").lower() != "false"
        return qs.filter(activo=activo)


class VehiculoViewSet(SoftDeleteMixin, viewsets.ModelViewSet):
    serializer_class = VehiculoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["patente", "marca", "modelo"]

    def get_queryset(self):
        qs = Vehiculo.objects.select_related("cliente").order_by("patente")
        activo = self.request.query_params.get("activo", "true").lower() != "false"
        qs = qs.filter(activo=activo)
        cliente = self.request.query_params.get("cliente")  # ?cliente=3
        if cliente:
            qs = qs.filter(cliente_id=cliente)
        return qs

