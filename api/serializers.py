from rest_framework import serializers

from catalogos.models import Servicio
from insumos.models import Insumo, Proveedor


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["id_proveedor", "nombre", "cuit", "telefono", "email"]


def _decimal():
    # Devuelve numeros (12.5) y no strings ("12.50"), como el contrato.
    return serializers.DecimalField(
        max_digits=10, decimal_places=2, min_value=0, coerce_to_string=False
    )


class InsumoSerializer(serializers.ModelSerializer):
    stock_actual = _decimal()
    stock_minimo = _decimal()
    costo_unitario = _decimal()

    class Meta:
        model = Insumo
        fields = [
            "id_insumo", "nombre", "unidad_medida",
            "stock_actual", "stock_minimo", "costo_unitario", "activo",
        ]


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio", "activo"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        }

