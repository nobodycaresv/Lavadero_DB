import re
from decimal import Decimal

from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers

from insumos.models import Compra, DetalleCompra, Insumo, MovimientoStock, Proveedor


class InsumoSerializer(serializers.ModelSerializer):
    stock_bajo = serializers.SerializerMethodField()

    class Meta:
        model = Insumo
        fields = [
            "id_insumo", "nombre", "unidad_medida", "stock_actual",
            "stock_minimo", "costo_unitario", "activo", "stock_bajo",
        ]
        read_only_fields = ["id_insumo"]
        extra_kwargs = {
            "stock_actual": {"min_value": 0},
            "stock_minimo": {"min_value": 0},
            "costo_unitario": {"min_value": 0},
        }

    def get_stock_bajo(self, insumo):
        return insumo.stock_actual <= insumo.stock_minimo

    def validate_nombre(self, value):
        value = re.sub(r"\s+", " ", value).strip()
        if not re.search(r"[^\W_]", value):
            raise serializers.ValidationError("El nombre debe tener letras o números.")
        otros = Insumo.objects.all()
        if self.instance is not None:
            otros = otros.exclude(pk=self.instance.pk)
        igual = next((i for i in otros if re.sub(r"\s+", " ", i.nombre).strip().casefold() == value.casefold()), None)
        if igual:
            pista = "" if igual.activo else " Está inactivo: activalo desde la lista."
            raise serializers.ValidationError("Ya existe un insumo con ese nombre." + pista)
        return value

    @transaction.atomic
    def create(self, validated_data):
        insumo = super().create(validated_data)
        if insumo.stock_actual > 0:
            MovimientoStock.objects.create(
                insumo=insumo, tipo_movimiento="entrada", cantidad=insumo.stock_actual,
                fecha=timezone.now(), motivo="Stock inicial",
            )
        return insumo

    def update(self, instance, validated_data):
        # El stock solo cambia con compras o consumos, nunca editándolo a mano.
        validated_data.pop("stock_actual", None)
        return super().update(instance, validated_data)


class MovimientoStockSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source="insumo.nombre", read_only=True)
    unidad_medida = serializers.CharField(source="insumo.unidad_medida", read_only=True)

    class Meta:
        model = MovimientoStock
        fields = [
            "id_movimiento", "insumo", "insumo_nombre", "unidad_medida",
            "tipo_movimiento", "cantidad", "fecha", "motivo",
        ]


class ConsumoSerializer(serializers.Serializer):
    """Datos de entrada para registrar un consumo (salida de stock)."""

    cantidad = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal("0.01"))
    motivo = serializers.CharField(max_length=50, required=False, allow_blank=True, default="Consumo")

    def registrar(self, insumo):
        cantidad = self.validated_data["cantidad"]
        motivo = self.validated_data["motivo"] or "Consumo"
        with transaction.atomic():
            # bloquea la fila para que dos consumos a la vez no dejen stock negativo
            insumo = Insumo.objects.select_for_update().get(pk=insumo.pk)
            if not insumo.activo:
                raise serializers.ValidationError({"insumo": "El insumo está desactivado."})
            if cantidad > insumo.stock_actual:
                raise serializers.ValidationError(
                    {"cantidad": f"Stock insuficiente: hay {insumo.stock_actual} {insumo.unidad_medida}."}
                )
            Insumo.objects.filter(pk=insumo.pk).update(stock_actual=F("stock_actual") - cantidad)
            return MovimientoStock.objects.create(
                insumo=insumo, tipo_movimiento="salida", cantidad=cantidad,
                fecha=timezone.now(), motivo=motivo,
            )


class DetalleCompraSerializer(serializers.ModelSerializer):
    insumo_nombre = serializers.CharField(source="insumo.nombre", read_only=True)

    class Meta:
        model = DetalleCompra
        fields = ["id_detalle_compra", "insumo", "insumo_nombre", "cantidad", "precio_unitario"]
        read_only_fields = ["id_detalle_compra"]
        extra_kwargs = {
            "cantidad": {"min_value": Decimal("0.01")},
            "precio_unitario": {"min_value": 0},
        }

    def validate_insumo(self, insumo):
        if not insumo.activo:
            raise serializers.ValidationError("El insumo está desactivado.")
        return insumo


class CompraSerializer(serializers.ModelSerializer):
    proveedor_nombre = serializers.CharField(source="proveedor.nombre", read_only=True)
    detalles = DetalleCompraSerializer(many=True)
    fecha = serializers.DateTimeField(required=False)

    class Meta:
        model = Compra
        fields = ["id_compra", "proveedor", "proveedor_nombre", "fecha", "total", "detalles"]
        read_only_fields = ["id_compra", "total"]

    def validate_detalles(self, detalles):
        if not detalles:
            raise serializers.ValidationError("La compra necesita al menos un insumo.")
        vistos = set()
        for detalle in detalles:
            insumo = detalle["insumo"]
            if insumo.pk in vistos:
                raise serializers.ValidationError(
                    f"El insumo {insumo.nombre} está repetido en la compra. Juntá las cantidades en una sola línea."
                )
            vistos.add(insumo.pk)
        return detalles

    @transaction.atomic
    def create(self, validated_data):
        detalles = validated_data.pop("detalles")
        fecha = validated_data.pop("fecha", None) or timezone.now()
        total = sum((d["cantidad"] * d["precio_unitario"] for d in detalles), Decimal("0"))
        compra = Compra.objects.create(fecha=fecha, total=total, **validated_data)
        for d in detalles:
            DetalleCompra.objects.create(compra=compra, **d)
            # la compra suma stock y deja el movimiento registrado
            Insumo.objects.filter(pk=d["insumo"].pk).update(stock_actual=F("stock_actual") + d["cantidad"])
            MovimientoStock.objects.create(
                insumo=d["insumo"], tipo_movimiento="entrada", cantidad=d["cantidad"],
                fecha=fecha, motivo=f"Compra #{compra.id_compra}",
            )
        return compra


class ProveedorOpcionSerializer(serializers.ModelSerializer):
    """Solo lo necesario para el selector de la pantalla de compras."""

    class Meta:
        model = Proveedor
        fields = ["id_proveedor", "nombre"]