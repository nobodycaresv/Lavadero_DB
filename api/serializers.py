from rest_framework import serializers
from catalogos.models import Servicio
from clientes.models import Convenio, Empresa


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio", "activo"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {"duracion": {"min_value": 1}, "precio": {"min_value": 0}}


class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ["id_empresa", "razon_social", "cuit", "email", "telefono", "activo"]
        read_only_fields = ["id_empresa"]
        extra_kwargs = {"email": {"error_messages": {"invalid": "Email inválido.", "blank": "El email es obligatorio."}}}

    def validate(self, data):
        for campo in ["razon_social", "cuit", "telefono"]:
            if campo in data:
                data[campo] = data[campo].strip()
                if not data[campo]:
                    raise serializers.ValidationError({campo: "Este campo no puede estar vacío."})

        if "cuit" in data:
            if sum(c.isdigit() for c in data["cuit"]) != 11:
                raise serializers.ValidationError({"cuit": "El CUIT debe tener 11 dígitos."})
            existe = Empresa.objects.filter(cuit=data["cuit"]).exclude(pk=getattr(self.instance, "pk", None)).exists()
            if existe:
                raise serializers.ValidationError({"cuit": "Ya existe una empresa con este CUIT."})

        if "telefono" in data and sum(c.isdigit() for c in data["telefono"]) < 10:
            raise serializers.ValidationError({"telefono": "El teléfono debe tener al menos 10 dígitos (código de área + número)."})


        return data


class ConvenioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Convenio
        fields = ["id_convenio", "empresa", "condiciones", "tipo_facturacion", "activo"]
        read_only_fields = ["id_convenio"]

    def validate(self, data):
        for campo in ["condiciones", "tipo_facturacion"]:
            if campo in data:
                data[campo] = data[campo].strip()
                if not data[campo]:
                    raise serializers.ValidationError({campo: "Este campo es obligatorio."})

        empresa = data.get("empresa")
        if empresa and not empresa.activo:
            if self.instance is None or self.instance.empresa_id != empresa.pk:
                raise serializers.ValidationError({"empresa": "No se puede asignar a una empresa dada de baja."})

        return data
