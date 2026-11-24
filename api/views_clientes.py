from rest_framework import filters, viewsets

from clientes.models import Cliente, Vehiculo

from .serializers_clientes import ClienteSerializer, VehiculoSerializer

class BajaLogicaViewSet(viewsets.ModelViewSet):
    """CRUD con baja lógica: DELETE solo marca activo=False, no borra de la base."""

    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        qs = super().get_queryset()
        # Por defecto devuelve todos. Con ?activo=true / ?activo=false filtra.
        activo = self.request.query_params.get("activo")
        if activo is not None:
            qs = qs.filter(activo=activo.lower() != "false")
        return qs

    def perform_destroy(self, instance):
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
        cliente = self.request.query_params.get("cliente")  # ej: /api/vehiculos?cliente=3
        return qs.filter(cliente_id=cliente) if cliente else qs