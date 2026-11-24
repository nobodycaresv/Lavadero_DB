from rest_framework import serializers

from catalogos.models import Estado, MedioPago, Servicio
from finanzas.models import Pago


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ["id_estado", "tipo", "nombre"]
        read_only_fields = ["id_estado"]


class MedioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedioPago
        fields = ["id_medio_pago", "nombre"]
        read_only_fields = ["id_medio_pago"]


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = [
            "id_pago",
            "factura",
            "medio_pago",
            "estado",
            "monto",
            "fecha_hora",
            "concepto",
            "pago_adelanto",
        ]
        read_only_fields = ["id_pago"]
        extra_kwargs = {
            "monto": {"min_value": 0},
        }


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio", "activo"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        }