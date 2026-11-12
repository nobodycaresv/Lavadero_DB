from rest_framework import serializers
from core.models import Estado, MedioPago

class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ["id_estado", "tipo", "nombre"]

class MedioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedioPago
        fields = ["id_medio_pago", "nombre"]