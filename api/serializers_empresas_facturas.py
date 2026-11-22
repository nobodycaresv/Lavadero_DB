import re
from rest_framework import serializers
from clientes.models import Cliente, Convenio, Empresa
from finanzas.models import Factura
from operaciones.models import OrdenTrabajo


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ["id_empresa", "razon_social", "cuit", "email", "telefono", "activo"]
        read_only_fields = ["id_empresa"]

    def validate_razon_social(self, value):
        valor = (value or "").strip()
        if not valor:
            raise serializers.ValidationError("La razón social es obligatoria.")
        return valor

    def validate_cuit(self, value):
        valor = (value or "").strip()
        if not re.match(r"^\d{11}$", valor):
            raise serializers.ValidationError("El CUIT debe tener exactamente 11 números, sin guiones ni espacios.")
        qs = Empresa.objects.filter(cuit=valor)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una empresa registrada con ese CUIT.")
        return valor

    def validate_email(self, value):
        valor = (value or "").strip()
        if not valor:
            raise serializers.ValidationError("El email es obligatorio.")
        return valor

    def validate_telefono(self, value):
        valor = (value or "").strip()
        if not re.match(r"^\d{7,13}$", valor):
            raise serializers.ValidationError("El teléfono debe contener solo números (entre 7 y 13 dígitos).")
        return valor


class ConvenioSerializer(serializers.ModelSerializer):
    empresa_nombre = serializers.CharField(source="empresa.razon_social", read_only=True)

    class Meta:
        model = Convenio
        fields = ["id_convenio", "empresa", "empresa_nombre", "condiciones", "tipo_facturacion", "activo"]
        read_only_fields = ["id_convenio", "empresa_nombre"]

    def validate_empresa(self, value):
        if not value.activo:
            if not self.instance or self.instance.empresa_id != value.id_empresa:
                raise serializers.ValidationError("No se puede asignar un convenio a una empresa inactiva.")
        return value

    def validate_tipo_facturacion(self, value):
        valor = (value or "").strip()
        if not valor:
            raise serializers.ValidationError("El tipo de facturación es obligatorio.")
        return valor

    def validate_condiciones(self, value):
        valor = (value or "").strip()
        if not valor:
            raise serializers.ValidationError("Las condiciones del convenio son obligatorias.")
        return valor


class FacturaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField(read_only=True)
    convenio_detalle = serializers.SerializerMethodField(read_only=True)
    email_destino = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Factura
        fields = [
            "id_factura",
            "cliente",
            "cliente_nombre",
            "convenio",
            "convenio_detalle",
            "orden",
            "numero_factura",
            "fecha_emision",
            "enviada_por_email",
            "email_destino",
            "total",
        ]
        read_only_fields = ["id_factura", "cliente_nombre", "convenio_detalle", "email_destino"]

    def get_cliente_nombre(self, obj):
        return f"{obj.cliente.nombre} {obj.cliente.apellido}"

    def get_convenio_detalle(self, obj):
        if not obj.convenio:
            return "Particular (sin convenio)"
        return f"{obj.convenio.empresa.razon_social} ({obj.convenio.tipo_facturacion})"

    def get_email_destino(self, obj):
        if obj.convenio and obj.convenio.empresa and obj.convenio.empresa.email:
            return obj.convenio.empresa.email
        return obj.cliente.email or ""

    def validate_numero_factura(self, value):
        valor = (value or "").strip()
        if not valor:
            raise serializers.ValidationError("El número de factura es obligatorio.")
        qs = Factura.objects.filter(numero_factura__iexact=valor)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe una factura con ese número.")
        return valor

    def validate_total(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("El total de la factura debe ser mayor a 0.")
        return value

    def validate(self, attrs):
        convenio = attrs.get("convenio", getattr(self.instance, "convenio", None))
        orden = attrs.get("orden", getattr(self.instance, "orden", None))

        if convenio and not convenio.activo:
            if not self.instance or self.instance.convenio_id != convenio.id_convenio:
                raise serializers.ValidationError({"convenio": "El convenio seleccionado está inactivo."})

        if orden:
            qs = Factura.objects.filter(orden=orden)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"orden": "Esta orden de trabajo ya tiene una factura emitida."})

        return attrs
