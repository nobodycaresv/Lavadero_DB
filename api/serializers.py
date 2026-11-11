from rest_framework import serializers

from core.models import Proveedor, Insumo


class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ["id_proveedor", "nombre", "telefono", "email"]


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