from rest_framework import serializers

from catalogos.models import Servicio
from clientes.models import Cliente, Vehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    # muestra el nombre del dueño sin tener que pedir el cliente aparte
    cliente_nombre = serializers.StringRelatedField(source="cliente", read_only=True)

    class Meta:
        model = Vehiculo
        fields = ["id_vehiculo", "cliente", "cliente_nombre", "patente", "marca", "modelo", "activo"]

    def validate_patente(self, value):  # pasa de "ab 123 cd" a "AB123CD"
        return value.replace(" ", "").replace("-", "").upper()


class ClienteSerializer(serializers.ModelSerializer):
    vehiculos = VehiculoSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = ["id_cliente", "nombre", "apellido", "telefono", "email", "activo", "vehiculos"]


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio", "activo"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        }