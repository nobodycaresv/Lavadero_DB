from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Servicio

from .serializers import ServicioSerializer


class EstadoAPIView(APIView):
    """Endpoint de ejemplo para confirmar que la API REST esta funcionando."""

    def get(self, request):
        return Response(
            {
                "estado": "ok",
                "mensaje": "La API REST del proyecto esta funcionando correctamente.",
            },
            status=status.HTTP_200_OK,
        )


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