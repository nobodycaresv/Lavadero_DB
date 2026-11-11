from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Convenio, Empresa, Servicio

from .serializers import ConvenioSerializer, EmpresaSerializer, ServicioSerializer


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


class EmpresaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Empresa.objects.all().order_by("id_empresa")
    serializer_class = EmpresaSerializer

    @action(detail=True, methods=["patch"])
    def desactivar(self, request, pk=None):
        empresa = self.get_object()
        empresa.activo = False
        empresa.save(update_fields=["activo"])
        # Al dar de baja la empresa, también se dan de baja sus convenios
        Convenio.objects.filter(empresa=empresa).update(activo=False)
        return Response(self.get_serializer(empresa).data)


class ConvenioViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Convenio.objects.select_related("empresa").order_by("id_convenio")
    serializer_class = ConvenioSerializer

    @action(detail=True, methods=["patch"])
    def desactivar(self, request, pk=None):
        convenio = self.get_object()
        convenio.activo = False
        convenio.save(update_fields=["activo"])
        return Response(self.get_serializer(convenio).data)