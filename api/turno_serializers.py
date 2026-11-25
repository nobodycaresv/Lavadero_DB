from rest_framework import serializers

from operaciones.models import Turno


class TurnoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source="cliente.nombre", read_only=True)
    cliente_apellido = serializers.CharField(source="cliente.apellido", read_only=True)
    cliente_telefono = serializers.CharField(source="cliente.telefono", read_only=True)
    cliente_email = serializers.CharField(source="cliente.email", read_only=True)
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    vehiculo_descripcion = serializers.SerializerMethodField()
    servicio_nombre = serializers.CharField(source="servicio.nombre_servicio", read_only=True)
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)

    class Meta:
        model = Turno
        fields = [
            "id_turno",
            "cliente",
            "cliente_nombre",
            "cliente_apellido",
            "cliente_telefono",
            "cliente_email",
            "vehiculo",
            "vehiculo_patente",
            "vehiculo_descripcion",
            "servicio",
            "servicio_nombre",
            "estado",
            "estado_nombre",
            "fecha",
            "hora",
        ]
        read_only_fields = ["id_turno"]

    def get_vehiculo_descripcion(self, obj: Turno) -> str:
        marca = (obj.vehiculo.marca or "").strip()
        modelo = (obj.vehiculo.modelo or "").strip()
        if modelo.lower() in ("", "sin especificar", "none"):
            base = marca
        else:
            base = f"{marca} {modelo}".strip()
        return f"{base} ({obj.vehiculo.patente})".strip()


class CrearTurnoSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=40)
    apellido = serializers.CharField(max_length=40)
    telefono = serializers.CharField(max_length=20)
    email = serializers.EmailField(max_length=100)
    patente = serializers.CharField(max_length=12)
    marca = serializers.CharField(max_length=40, required=False, allow_blank=True, default="Sin especificar")
    servicio_id = serializers.IntegerField(min_value=1)
    fecha = serializers.DateField()
    hora = serializers.TimeField()


class ConfirmarValidacionTurnoSerializer(serializers.Serializer):
    aceptado = serializers.BooleanField(default=True)


class CambiarEstadoTurnoSerializer(serializers.Serializer):
    estado = serializers.CharField(max_length=40)