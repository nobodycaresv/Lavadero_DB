from rest_framework import serializers

from clientes.models import Cliente, Vehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    # muestra el nombre del dueño sin tener que pedir el cliente aparte
    cliente_nombre = serializers.StringRelatedField(source="cliente", read_only=True)

    class Meta:
        model = Vehiculo
        fields = ["id_vehiculo", "cliente", "cliente_nombre", "patente", "marca", "modelo", "activo"]

    def validate_patente(self, value):
        # pasa de "ab 123-cd" a "AB123CD"
        return value.replace(" ", "").replace("-", "").upper()


class ClienteSerializer(serializers.ModelSerializer):
    # solo los vehículos activos del cliente
    vehiculos = serializers.SerializerMethodField()

    class Meta:
        model = Cliente
        fields = ["id_cliente", "nombre", "apellido", "telefono", "email", "activo", "vehiculos"]

    def get_vehiculos(self, cliente):
        activos = [v for v in cliente.vehiculos.all() if v.activo]
        return VehiculoSerializer(activos, many=True).data