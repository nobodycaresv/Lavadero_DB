from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from insumos.models import Compra, Insumo, MovimientoStock, Proveedor

from .serializers_insumos import (
    CompraSerializer,
    ConsumoSerializer,
    InsumoSerializer,
    MovimientoStockSerializer,
    ProveedorOpcionSerializer,
)


class InsumoViewSet(viewsets.ModelViewSet):
    queryset = Insumo.objects.all().order_by("nombre")
    serializer_class = InsumoSerializer

    def perform_destroy(self, instance):
        # baja lógica: el insumo queda inactivo, no se borra de la base
        instance.activo = False
        instance.save(update_fields=["activo"])

    @action(detail=True, methods=["post"])
    def consumir(self, request, pk=None):
        """POST /api/insumos/<id>/consumir  {cantidad, motivo}  -> resta stock."""
        insumo = self.get_object()
        entrada = ConsumoSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        movimiento = entrada.registrar(insumo)
        return Response(MovimientoStockSerializer(movimiento).data, status=201)


class MovimientoStockViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Historial de entradas y salidas de stock (solo lectura)."""

    queryset = MovimientoStock.objects.select_related("insumo").order_by("-fecha", "-id_movimiento")
    serializer_class = MovimientoStockSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        insumo = self.request.query_params.get("insumo")
        return qs.filter(insumo_id=insumo) if insumo else qs


class CompraViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Las compras se registran y se consultan. No se editan ni se borran porque ya movieron stock."""

    queryset = Compra.objects.select_related("proveedor").prefetch_related("detalles__insumo").order_by("-fecha", "-id_compra")
    serializer_class = CompraSerializer

    @action(detail=False, methods=["get"])
    def opciones(self, request):
        """GET /api/compras/opciones -> proveedores e insumos activos para armar el formulario."""
        insumos = Insumo.objects.filter(activo=True).order_by("nombre")
        return Response({
            "proveedores": ProveedorOpcionSerializer(Proveedor.objects.order_by("nombre"), many=True).data,
            "insumos": InsumoSerializer(insumos, many=True).data,
        })