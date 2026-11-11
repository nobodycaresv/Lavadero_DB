from rest_framework import serializers

from core.models import Servicio


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio", "activo"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        }

from rest_framework import serializers

from core.models import Empleado

class EmpleadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empleado
        fields = ["id_empleado", "nombre", "apellido", "rol", "activo"]