from rest_framework import serializers

from core.models import Convenio, Empresa, Servicio


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio", "activo"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        }


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ["id_empresa", "razon_social", "cuit", "email", "telefono", "activo"]
        read_only_fields = ["id_empresa"]

    def validate_cuit(self, value):
        digitos = [c for c in value if c.isdigit()]
        if len(digitos) != 11:
            raise serializers.ValidationError("El CUIT debe tener 11 dígitos.")
        return value


class ConvenioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convenio
        fields = ["id_convenio", "empresa", "condiciones", "tipo_facturacion", "activo"]
        read_only_fields = ["id_convenio"]

    def validate_empresa(self, value):
        # No permite asignar el convenio a una empresa dada de baja
        # (pero sí editar un convenio que ya pertenecía a ella).
        cambio_de_empresa = self.instance is None or self.instance.empresa_id != value.pk
        if not value.activo and cambio_de_empresa:
            raise serializers.ValidationError("La empresa está dada de baja.")
        return value