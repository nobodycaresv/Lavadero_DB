from rest_framework import filters, viewsets
from core.models import Estado, MedioPago
from .serializers import EstadoSerializer, MedioPagoSerializer

class EstadoViewSet(viewsets.ModelViewSet):
    """
    Catálogo de estados (permite filtrar opcionalmente por tipo: 
    ej. /api/estados/?tipo=turno tal como indica el contrato de la API).
    """
    serializer_class = EstadoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["tipo", "nombre"]

    def get_queryset(self):
        qs = Estado.objects.order_by("tipo", "nombre")
        tipo = self.request.query_params.get("tipo")
        if tipo:
            qs = qs.filter(tipo__iexact=tipo)
        return qs


class MedioPagoViewSet(viewsets.ModelViewSet):
    """
    Catálogo de medios de pago disponibles en el sistema.
    """
    serializer_class = MedioPagoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre"]

    def get_queryset(self):
        return MedioPago.objects.order_by("nombre")