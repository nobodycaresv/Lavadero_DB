import re

from rest_framework import serializers

from clientes.models import Cliente, Vehiculo

# Patente argentina formato nuevo (AB123CD) o formato viejo (ABC123)
PATENTE_REGEX = re.compile(r"^(?:[A-Z]{2}\d{3}[A-Z]{2}|[A-Z]{3}\d{3})$")

# Nombre/apellido solo letras (con tildes y ñ), espacios, apóstrofe, punto y guion
NOMBRE_REGEX = re.compile(r"^[^\W\d_]+(?:[ '.\-][^\W\d_]+)*\.?$")

# Marca/modelo letras, números, espacios y . - /
MARCA_MODELO_REGEX = re.compile(r"^[\w .\-/]+$")

PARTICULAS = {"de", "del", "la", "las", "los", "y", "da", "di", "van", "von"}


def juntar_espacios(texto):
    return re.sub(r"\s+", " ", str(texto)).strip()


def capitalizar_nombre(texto):
    """'juan  carlos DE la cruz' -> 'Juan Carlos de la Cruz'."""
    palabras = []
    for i, palabra in enumerate(juntar_espacios(texto).lower().split(" ")):
        if i > 0 and palabra in PARTICULAS:
            palabras.append(palabra)
        else:
            palabras.append(re.sub(r"(^|[-'])([^\W\d_])", lambda m: m.group(1) + m.group(2).upper(), palabra))
    return " ".join(palabras)


def desactivar_cliente(cliente):
    """Baja lógica del cliente y de todos sus vehículos activos. Devuelve cuántos vehículos se dieron de baja."""
    cantidad = cliente.vehiculos.filter(activo=True).update(activo=False)
    cliente.activo = False
    cliente.save(update_fields=["activo"])
    return cantidad


class VehiculoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.StringRelatedField(source="cliente", read_only=True)

    class Meta:
        model = Vehiculo
        fields = ["id_vehiculo", "cliente", "cliente_nombre", "patente", "marca", "modelo", "activo"]
        # La unicidad de la patente se controla en validate_patente (ya normalizada)
        extra_kwargs = {"patente": {"validators": []}}

    def validate_patente(self, value):
        patente = value.replace(" ", "").replace("-", "").upper()
        if not PATENTE_REGEX.match(patente):
            raise serializers.ValidationError("Patente inválida. Usá el formato nuevo (AB123CD) o el viejo (ABC123).")
        repetidas = Vehiculo.objects.filter(patente=patente)
        if self.instance is not None:
            repetidas = repetidas.exclude(pk=self.instance.pk)
        if repetidas.exists():
            raise serializers.ValidationError("Ya existe un vehículo con esa patente.")
        return patente

    def _validar_texto(self, value, campo):
        value = juntar_espacios(value)
        if not MARCA_MODELO_REGEX.match(value) or not re.search(r"[^\W_]", value):
            raise serializers.ValidationError(f"{campo} inválido. Usá solo letras, números, espacios, punto o guion.")
        return value

    def validate_marca(self, value):
        return self._validar_texto(value, "Marca")

    def validate_modelo(self, value):
        return self._validar_texto(value, "Modelo")

    def validate(self, attrs):
        cliente = attrs.get("cliente")
        reactivando = self.instance is not None and attrs.get("activo") is True and not self.instance.activo
        cambia_duenio = self.instance is None or (cliente is not None and cliente != self.instance.cliente)
        # Un vehículo activo no puede quedar a nombre de un cliente inactivo
        if cliente is None and self.instance is not None:
            cliente = self.instance.cliente
        if cliente is not None and not cliente.activo and (cambia_duenio or reactivando):
            raise serializers.ValidationError(
                {"cliente": "El dueño está inactivo. Activá primero al cliente o elegí otro dueño."}
            )
        return attrs


class ClienteSerializer(serializers.ModelSerializer):
    vehiculos = serializers.SerializerMethodField()   # solo los activos

    class Meta:
        model = Cliente
        fields = ["id_cliente", "nombre", "apellido", "telefono", "email", "activo", "vehiculos"]

    def get_vehiculos(self, cliente):
        activos = [v for v in cliente.vehiculos.all() if v.activo]
        return VehiculoSerializer(activos, many=True).data

    def _validar_nombre(self, value, campo):
        value = juntar_espacios(value)
        if not NOMBRE_REGEX.match(value):
            raise serializers.ValidationError(f"{campo} inválido. Usá solo letras (sin números ni símbolos).")
        return capitalizar_nombre(value)

    def validate_nombre(self, value):
        return self._validar_nombre(value, "Nombre")

    def validate_apellido(self, value):
        return self._validar_nombre(value, "Apellido")

    def validate_telefono(self, value):
        value = juntar_espacios(value)
        if not re.match(r"^\+?[\d\s()\-]+$", value):
            raise serializers.ValidationError("Teléfono inválido. Usá solo números, espacios, + - ( ).")
        digitos = re.sub(r"\D", "", value)
        if not 8 <= len(digitos) <= 15:
            raise serializers.ValidationError("El teléfono debe tener entre 8 y 15 dígitos.")
        return ("+" if value.startswith("+") else "") + digitos

    def validate_email(self, value):
        return value.strip().lower()

    def validate(self, attrs):
        def dato(campo):
            return attrs[campo] if campo in attrs else getattr(self.instance, campo, "")

        otros = Cliente.objects.all()
        if self.instance is not None:
            otros = otros.exclude(pk=self.instance.pk)

        # Duplicado exacto (incluye clientes inactivos): se rechaza
        if {"nombre", "apellido", "telefono"} & set(attrs):
            igual = otros.filter(
                nombre__iexact=dato("nombre"), apellido__iexact=dato("apellido"), telefono=dato("telefono")
            ).first()
            if igual:
                estado = "" if igual.activo else " (está inactivo: activalo desde la lista)"
                raise serializers.ValidationError(
                    {"non_field_errors": [f"Ya existe un cliente con el mismo nombre, apellido y teléfono{estado}."]}
                )

        # Mismo teléfono o email que otra persona se permite, pero se avisa
        avisos = []
        if "telefono" in attrs:
            otro = otros.filter(telefono=attrs["telefono"]).first()
            if otro:
                avisos.append(f"Ojo: el teléfono ya lo tiene {otro.apellido}, {otro.nombre}.")
        if attrs.get("email"):
            otro = otros.filter(email__iexact=attrs["email"]).first()
            if otro:
                avisos.append(f"Ojo: el correo ya lo tiene {otro.apellido}, {otro.nombre}.")
        self._avisos = avisos
        return attrs

    def update(self, instance, validated_data):
        # Al desactivar un cliente también se dan de baja sus vehículos
        if validated_data.get("activo") is False and instance.activo:
            instance.vehiculos.filter(activo=True).update(activo=False)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if getattr(self, "_avisos", None):
            data["avisos"] = self._avisos
        return data