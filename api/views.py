from rest_framework import filters, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Cliente, Vehiculo
from .serializers import ClienteSerializer, VehiculoSerializer

class EstadoAPIView(APIView):
    def get(self, request):
        return Response({"estado": "ok", "mensaje": "La API REST del proyecto esta funcionando correctamente."})

class BajaLogicaViewSet(viewsets.ModelViewSet):
    #CRUD base con baja lógica (activo=False)

    filter_backends = [filters.SearchFilter]

    def get_queryset(self):
        activo = self.request.query_params.get("activo", "true").lower() != "false" # en pocas palabras, si no viene activo=false, devuelve solo activos
        return self.queryset.filter(activo=activo)

    def perform_destroy(self, instance): # de ejecuta solo para el delete y solo lo marca como inactivo y no borra en la base de datos
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
        cliente = self.request.query_params.get("cliente")  # ?cliente=3
        return qs.filter(cliente_id=cliente) if cliente else qs