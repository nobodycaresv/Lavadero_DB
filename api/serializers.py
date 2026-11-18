from rest_framework import serializers
<<<<<<< HEAD
from core.models import Estado, MedioPago

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ["id_estado", "tipo", "nombre"]

class MedioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedioPago
        fields = ["id_medio_pago", "nombre"]
=======

from catalogos.models import Servicio


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio", "activo"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        } 
>>>>>>> 321c9615e00bfe9f1b5585bc4d4f155548942d22
