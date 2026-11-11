from django.db.models import ProtectedError
from rest_framework import filters, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Proveedor, Insumo

from .serializers import ProveedorSerializer, InsumoSerializer


class EstadoAPIView(APIView):
    """
    Endpoint de ejemplo para confirmar que la API REST esta funcionando.

    Prueben visitarlo desde el navegador en:
        http://localhost:8000/api/estado/
    """

    def get(self, request):
        return Response(
            {
                "estado": "ok",
                "mensaje": "La API REST del proyecto esta funcionando correctamente.",
            },
            status=status.HTTP_200_OK,
        )


class ProveedorViewSet(viewsets.ModelViewSet):
    """
    Proveedor no tiene campo 'activo' en el DER, asi que la baja es DELETE.
    Si tiene compras asociadas (on_delete=PROTECT) no se puede borrar -> 409.
    """
    serializer_class = ProveedorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "telefono", "email"]

    def get_queryset(self):
        return Proveedor.objects.order_by("nombre")

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detalle": "No se puede dar de baja: el proveedor tiene compras asociadas."},
                status=status.HTTP_409_CONFLICT,
            )


class InsumoViewSet(viewsets.ModelViewSet):
    """
    Insumo si tiene 'activo': el DELETE hace baja logica (activo=False).
    Por defecto lista solo activos; ?activo=false para ver los dados de baja.
    """
    serializer_class = InsumoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nombre", "unidad_medida"]

    def get_queryset(self):
        qs = Insumo.objects.order_by("nombre")
        activo = self.request.query_params.get("activo", "true").lower() != "false"
        return qs.filter(activo=activo)

    def perform_destroy(self, instance):
        instance.activo = False
        instance.save(update_fields=["activo"])