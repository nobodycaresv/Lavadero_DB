from django.db.models.deletion import ProtectedError
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from catalogos.models import Estado
from operaciones.models import DetalleServicio, FichaTecnica, OrdenTrabajo, Turno

from .operaciones_serializers import (
    DetalleServicioSerializer,
    FichaTecnicaSerializer,
    OrdenTrabajoSerializer,
)


class FichaTecnicaViewSet(viewsets.ModelViewSet):
    queryset = FichaTecnica.objects.select_related(
        "turno", "turno__vehiculo", "empleado"
    ).order_by("-id_ficha")
    serializer_class = FichaTecnicaSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "No se puede eliminar la ficha porque ya tiene una orden de trabajo asociada."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def turnos(self, request):
        """Lista los turnos para el selector de fichas sin depender todavía del endpoint de Turnos."""
        turnos = Turno.objects.select_related("cliente", "vehiculo", "servicio").order_by("-fecha", "-hora")
        data = [
            {
                "id_turno": t.id_turno,
                "label": f"{t} - {t.cliente} ({t.fecha} {str(t.hora)[:5]})",
                "tiene_ficha": hasattr(t, "ficha_tecnica"),
            }
            for t in turnos
        ]
        return Response(data)


class OrdenTrabajoViewSet(viewsets.ModelViewSet):
    queryset = (
        OrdenTrabajo.objects.select_related(
            "ficha_tecnica",
            "ficha_tecnica__turno",
            "ficha_tecnica__turno__vehiculo",
            "estado",
        )
        .prefetch_related("detalles_servicio")
        .order_by("-id_orden")
    )
    serializer_class = OrdenTrabajoSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "No se puede eliminar la orden porque tiene servicios o facturas asociadas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"])
    def estados(self, request):
        """Lista los estados de tipo 'orden' para el selector de órdenes."""
        estados = Estado.objects.filter(tipo="orden").order_by("id_estado")
        return Response([{"id_estado": e.id_estado, "nombre": e.nombre} for e in estados])


class DetalleServicioViewSet(viewsets.ModelViewSet):
    serializer_class = DetalleServicioSerializer

    def get_queryset(self):
        qs = DetalleServicio.objects.select_related("orden", "servicio", "empleado").order_by("id_detalle")
        orden_id = self.request.query_params.get("orden")
        if orden_id:
            qs = qs.filter(orden_id=orden_id)
        return qs

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detail": "No se puede quitar el detalle porque tiene consumos de insumos registrados."},
                status=status.HTTP_400_BAD_REQUEST,
            )