from rest_framework import filters, viewsets

from core.models import Empleado
from .serializers import EmpleadoSerializer

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