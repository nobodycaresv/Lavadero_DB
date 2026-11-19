import re
from rest_framework import serializers
from catalogos.models import Estado, MedioPago, Servicio


def validar_texto_catalogo(value, campo="nombre"):
    limpio = " ".join(value.strip().split())

    if len(limpio) < 3:
        raise serializers.ValidationError(
            f"El {campo} debe tener al menos 3 caracteres."
        )

    # Solo permite letras, espacios y guiones (evita símbolos raros o números sueltos)
    if not re.fullmatch(r"[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-]+", limpio):
        raise serializers.ValidationError(
            f"El {campo} solo puede contener letras y espacios."
        )

    # Evita repeticiones absurdas como "aaaa" o "ssss"
    if re.search(r"(.)\1{2,}", limpio.lower()):
        raise serializers.ValidationError(
            f"El {campo} contiene caracteres repetidos no válidos."
        )

    # Verifica cada palabra para rechazar cadenas aleatorias de teclado (ej: "lasmflamfñ", "asdsad")
    for palabra in limpio.split(" "):
        p = palabra.lower()
        vocales = re.findall(r"[aeiouáéíóú]", p)
        if len(p) >= 3 and len(vocales) == 0:
            raise serializers.ValidationError(
                f"Ingresá un {campo} válido."
            )
        if len(p) >= 6 and len(vocales) / len(p) < 0.25:
            raise serializers.ValidationError(
                f"Ingresá un {campo} válido (sin texto aleatorio)."
            )

    return limpio


class EstadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estado
        fields = ["id_estado", "tipo", "nombre"]

    def validate_nombre(self, value):
        limpio = validar_texto_catalogo(value, campo="nombre del estado")
        tipo = self.initial_data.get("tipo", "").strip().lower()
        if Estado.objects.filter(tipo__iexact=tipo, nombre__iexact=limpio).exists():
            raise serializers.ValidationError(
                "Ya existe un estado con ese nombre para ese tipo."
            )
        return limpio


class MedioPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedioPago
        fields = ["id_medio_pago", "nombre"]

    def validate_nombre(self, value):
        limpio = validar_texto_catalogo(value, campo="medio de pago")
        if MedioPago.objects.filter(nombre__iexact=limpio).exists():
            raise serializers.ValidationError(
                "Ese medio de pago ya está registrado."
            )
        return limpio


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = ["id_servicio", "nombre_servicio", "duracion", "precio"]
        read_only_fields = ["id_servicio"]
        extra_kwargs = {
            "duracion": {"min_value": 1},
            "precio": {"min_value": 0},
        }