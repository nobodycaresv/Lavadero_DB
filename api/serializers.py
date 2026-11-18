from rest_framework import serializers
from catalogos.models import Estado, Servicio
from finanzas.models import MedioPago

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ["id_estado", "tipo", "nombre"]

class MedioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedioPago
        fields = ["id_medio_pago", "nombre"]

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        }