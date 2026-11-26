from datetime import datetime

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from catalogos.models import Estado
from operaciones.models import Turno
from operaciones.services import (
    DURACION_BLOQUE_HORAS,
    HORARIOS_DISPONIBLES,
    cambiar_estado_turno,
    confirmar_turno_desde_validacion,
    construir_mensaje_whatsapp,
    crear_turno,
    sumar_un_mes_calendario,
)
from django.utils import timezone

from .turno_serializers import (
    CambiarEstadoTurnoSerializer,
    ConfirmarValidacionTurnoSerializer,
    CrearTurnoSerializer,
    TurnoSerializer,
)


class TurnoViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = (
        Turno.objects.select_related("cliente", "vehiculo", "servicio", "estado")
        .all()
        .order_by("-fecha", "hora", "-id_turno")
    )
    serializer_class = TurnoSerializer

    def get_permissions(self):
        # Públicas: reservar y ver disponibilidad (formulario de la web).
        # El resto (listar, ver, cambiar estado, cancelar) es solo para el personal.
        if self.action in ("create", "disponibilidad"):
            return [AllowAny()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        serializer = CrearTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            resultado = crear_turno(**serializer.validated_data)
        except DjangoValidationError as exc:
            detalle = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            return Response({"detalle": detalle}, status=status.HTTP_400_BAD_REQUEST)

        turno = resultado["turno"]
        return Response(
            {
                "turno": TurnoSerializer(turno).data,
                "validacion_whatsapp": resultado["validacion_whatsapp"],
                "mensaje": "Turno registrado en estado 'pendiente'. Enviá la validación por WhatsApp para que el usuario confirme.",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="confirmar-validacion")
    def confirmar_validacion(self, request, pk=None):
        """Cambia el turno de 'pendiente' a 'confirmado' cuando el usuario acepta la validación."""
        serializer = ConfirmarValidacionTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            turno = confirmar_turno_desde_validacion(
                turno_id=int(pk),
                aceptado_por_usuario=serializer.validated_data["aceptado"],
            )
        except DjangoValidationError as exc:
            detalle = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            return Response({"detalle": detalle}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "turno": TurnoSerializer(turno).data,
                "validacion_whatsapp": construir_mensaje_whatsapp(turno),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"], url_path="estado")
    def actualizar_estado(self, request, pk=None):
        """Permite cambiar estado (pendiente / confirmado / cancelado) respetando reglas."""
        serializer = CambiarEstadoTurnoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            turno = cambiar_estado_turno(
                turno_id=int(pk),
                nuevo_estado_nombre=serializer.validated_data["estado"],
            )
        except DjangoValidationError as exc:
            detalle = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            return Response({"detalle": detalle}, status=status.HTTP_400_BAD_REQUEST)

        return Response(TurnoSerializer(turno).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"], url_path="cancelar")
    def cancelar(self, request, pk=None):
        """Cancela el turno sin usar DELETE físico en la base de datos."""
        try:
            turno = cambiar_estado_turno(turno_id=int(pk), nuevo_estado_nombre="cancelado")
        except DjangoValidationError as exc:
            detalle = exc.message_dict if hasattr(exc, "message_dict") else exc.messages
            return Response({"detalle": detalle}, status=status.HTTP_400_BAD_REQUEST)

        return Response(TurnoSerializer(turno).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="disponibilidad")
    def disponibilidad(self, request):
        """
        Devuelve los bloques de 2 horas (09:00 a 19:00) para una fecha dada (YYYY-MM-DD)
        indicando cuáles están ocupados y la fecha máxima permitida (1 mes desde hoy).
        """
        fecha_str = request.query_params.get("fecha")
        hoy = timezone.localdate()
        fecha_maxima = sumar_un_mes_calendario(hoy)

        if not fecha_str:
            return Response(
                {
                    "hoy": hoy.isoformat(),
                    "fecha_maxima": fecha_maxima.isoformat(),
                    "bloques": [],
                },
                status=status.HTTP_200_OK,
            )

        try:
            fecha_consultada = datetime.strptime(fecha_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detalle": "Formato de fecha inválido. Usá YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        estado_cancelado = Estado.objects.filter(tipo="turno", nombre__iexact="cancelado").first()
        ocupados_qs = Turno.objects.filter(fecha=fecha_consultada)
        if estado_cancelado:
            ocupados_qs = ocupados_qs.exclude(estado=estado_cancelado)
        horas_ocupadas = {t.hora.strftime("%H:%M") for t in ocupados_qs}

        fuera_de_rango = fecha_consultada < hoy or fecha_consultada > fecha_maxima
        bloques = []
        for hora_inicio in HORARIOS_DISPONIBLES:
            hora_fin = hora_inicio.replace(hour=(hora_inicio.hour + DURACION_BLOQUE_HORAS) % 24)
            inicio_str = hora_inicio.strftime("%H:%M")
            fin_str = hora_fin.strftime("%H:%M")
            ocupado = inicio_str in horas_ocupadas
            bloques.append(
                {
                    "inicio": inicio_str,
                    "fin": fin_str,
                    "etiqueta": f"{inicio_str} - {fin_str}",
                    "ocupado": ocupado,
                    "disponible": (not ocupado) and (not fuera_de_rango),
                }
            )

        return Response(
            {
                "fecha": fecha_consultada.isoformat(),
                "hoy": hoy.isoformat(),
                "fecha_maxima": fecha_maxima.isoformat(),
                "fuera_de_rango": fuera_de_rango,
                "bloques": bloques,
            },
            status=status.HTTP_200_OK,
        )