from decimal import Decimal
from rest_framework import serializers

from operaciones.models import DetalleServicio, FichaTecnica, OrdenTrabajo


class FichaTecnicaSerializer(serializers.ModelSerializer):
    turno_texto = serializers.SerializerMethodField()
    empleado_nombre = serializers.SerializerMethodField()
    tiene_orden = serializers.SerializerMethodField()

    class Meta:
        model = FichaTecnica
        fields = [
            "id_ficha",
            "turno",
            "turno_texto",
            "empleado",
            "empleado_nombre",
            "fecha_hora_ingreso",
            "estado_pintura",
            "estado_vidrios",
            "estado_opticas",
            "observaciones",
            "danos_preexistentes",
            "confirmada",
            "tiene_orden",
        ]
        read_only_fields = ["id_ficha", "turno_texto", "empleado_nombre", "tiene_orden"]

    def get_turno_texto(self, obj):
        return f"{obj.turno} ({obj.turno.fecha} {str(obj.turno.hora)[:5]})"

    def get_empleado_nombre(self, obj):
        return str(obj.empleado)

    def get_tiene_orden(self, obj):
        return hasattr(obj, "orden_trabajo")

    def _validar_texto(self, value, campo):
        limpio = value.strip()
        if not limpio:
            raise serializers.ValidationError(f"El campo {campo} no puede estar vacío.")
        return limpio

    def validate_estado_pintura(self, value):
        return self._validar_texto(value, "estado de pintura")

    def validate_estado_vidrios(self, value):
        return self._validar_texto(value, "estado de vidrios")

    def validate_estado_opticas(self, value):
        return self._validar_texto(value, "estado de ópticas")

    def validate_empleado(self, value):
        if not value.activo:
            if self.instance and self.instance.empleado_id == value.id_empleado:
                return value
            raise serializers.ValidationError("El empleado seleccionado está inactivo.")
        return value

    def validate_confirmada(self, value):
        if self.instance and not value and hasattr(self.instance, "orden_trabajo"):
            raise serializers.ValidationError(
                "No se puede desconfirmar una ficha que ya tiene una orden de trabajo asociada."
            )
        return value


class DetalleServicioSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source="servicio.nombre_servicio", read_only=True)
    empleado_nombre = serializers.SerializerMethodField()

    class Meta:
        model = DetalleServicio
        fields = [
            "id_detalle",
            "orden",
            "servicio",
            "servicio_nombre",
            "empleado",
            "empleado_nombre",
            "hora_fin",
            "precio",
        ]
        read_only_fields = ["id_detalle", "servicio_nombre", "empleado_nombre"]
        extra_kwargs = {
            "precio": {"min_value": Decimal("0.00")},
            "hora_fin": {"required": False, "allow_null": True},
        }

    def get_empleado_nombre(self, obj):
        return str(obj.empleado)

    def validate_servicio(self, value):
        if not value.activo:
            if self.instance and self.instance.servicio_id == value.id_servicio:
                return value
            raise serializers.ValidationError("El servicio seleccionado está inactivo.")
        return value

    def validate_empleado(self, value):
        if not value.activo:
            if self.instance and self.instance.empleado_id == value.id_empleado:
                return value
            raise serializers.ValidationError("El empleado seleccionado está inactivo.")
        return value

    def validate(self, attrs):
        orden = attrs.get("orden") or (self.instance.orden if self.instance else None)
        hora_fin = attrs.get("hora_fin", self.instance.hora_fin if self.instance else None)
        if orden and hora_fin and hora_fin < orden.hora_inicio:
            raise serializers.ValidationError(
                {"hora_fin": "La hora de finalización no puede ser anterior a la hora de inicio de la orden."}
            )
        return attrs


class OrdenTrabajoSerializer(serializers.ModelSerializer):
    ficha_texto = serializers.SerializerMethodField()
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    cantidad_servicios = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    class Meta:
        model = OrdenTrabajo
        fields = [
            "id_orden",
            "ficha_tecnica",
            "ficha_texto",
            "estado",
            "estado_nombre",
            "hora_inicio",
            "cantidad_servicios",
            "total",
        ]
        read_only_fields = ["id_orden", "ficha_texto", "estado_nombre", "cantidad_servicios", "total"]

    def get_ficha_texto(self, obj):
        return f"Ficha #{obj.ficha_tecnica_id} - {obj.ficha_tecnica.turno}"

    def get_cantidad_servicios(self, obj):
        return obj.detalles_servicio.count()

    def get_total(self, obj):
        total = sum((d.precio for d in obj.detalles_servicio.all()), Decimal("0.00"))
        return float(total)

    def validate_ficha_tecnica(self, value):
        if not value.confirmada:
            raise serializers.ValidationError(
                "La ficha técnica debe estar confirmada antes de crear una orden de trabajo."
            )
        return value

    def validate_estado(self, value):
        if value.tipo != "orden":
            raise serializers.ValidationError("El estado seleccionado debe corresponder al tipo 'orden'.")
        return value