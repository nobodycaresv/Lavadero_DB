from rest_framework import filters, viewsets
from django.shortcuts import render
from catalogos.models import Estado, MedioPago, Servicio
from .serializers import EstadoSerializer, MedioPagoSerializer, ServicioSerializer


class EstadoViewSet(viewsets.ModelViewSet):
    """
    Catálogo de estados activos (permite filtrar opcionalmente por tipo:
    ej. /api/estados/?tipo=turno tal como indica el contrato de la API).
    """

    serializer_class = EstadoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["tipo", "nombre"]

    def get_queryset(self):
        qs = Estado.objects.filter(activo=True).order_by("tipo", "nombre")
        tipo = self.request.query_params.get("tipo")
        if tipo:
            qs = qs.filter(tipo__iexact=tipo)
        return qs


class MedioPagoViewSet(viewsets.ModelViewSet):
    """
    Catálogo de medios de pago activos disponibles en el sistema.
    """

    serializer_class = MedioPagoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre"]

    def get_queryset(self):
        return MedioPago.objects.filter(activo=True).order_by("nombre")


class ServicioViewSet(viewsets.ModelViewSet):
    """
    Catálogo de servicios activos disponibles en el lavadero.
    """

    serializer_class = ServicioSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre_servicio"]

    def get_queryset(self):
        return Servicio.objects.filter(activo=True).order_by("nombre_servicio")


def panel_gestion(request):
    """
    Vista propia en HTML con la identidad visual de Rosario Estética Vehicular.
    """
    return render(request, "api/gestion.html")