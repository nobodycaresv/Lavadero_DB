from rest_framework import serializers

from core.models import Cliente, Vehiculo


class VehiculoSerializer(serializers.ModelSerializer):
    # Solo lectura: muestra el nombre del dueño sin tener que pedir el cliente aparte
    cliente_nombre = serializers.StringRelatedField(source="cliente", read_only=True)

    class Meta:
        model = Vehiculo
        fields = ["id_vehiculo", "cliente", "cliente_nombre", "patente", "marca", "modelo", "activo"]

    def validate_patente(self, value):
        #  junta los espacios y pasa de "ab 123 cd" a "AB123CD"
        return value.replace(" ", "").replace("-", "").upper()


class ClienteSerializer(serializers.ModelSerializer):
    # Vehículos anidados, solo lectura (para crearlos se usa /api/vehiculos/)
    vehiculos = VehiculoSerializer(many=True, read_only=True)

    class Meta:
        model = Cliente
        fields = ["id_cliente", "nombre", "apellido", "telefono", "email", "activo", "vehiculos"]
