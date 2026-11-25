import calendar
from datetime import date, time
import re
from urllib.parse import quote

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from catalogos.models import Estado, Servicio
from clientes.models import Cliente, Vehiculo
from operaciones.models import Turno


# Bloques de 2 horas dentro de la franja 09:00 a 19:00
HORARIOS_DISPONIBLES = [
    time(9, 0),
    time(11, 0),
    time(13, 0),
    time(15, 0),
    time(17, 0),
]

DURACION_BLOQUE_HORAS = 2

RE_NOMBRE_APELLIDO = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*$")
RE_EMAIL = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
RE_TELEFONO = re.compile(r"^\+?[0-9]{6,15}$")
RE_PATENTE = re.compile(r"^[A-Z0-9]{6,8}$")
RE_MARCA = re.compile(r"^[A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]+(?: [A-Za-z0-9ÁÉÍÓÚÜÑáéíóúüñ]+)*$")


def colapsar_espacios(valor: str) -> str:
    """Quita espacios a los extremos y reduce espacios múltiples internos a uno solo."""
    return " ".join((valor or "").strip().split())


def sumar_un_mes_calendario(fecha_base: date) -> date:
    """Devuelve la misma fecha un mes calendario adelante (ajustando fin de mes si hace falta)."""
    anio = fecha_base.year + (fecha_base.month // 12)
    mes = (fecha_base.month % 12) + 1
    ultimo_dia_mes = calendar.monthrange(anio, mes)[1]
    dia = min(fecha_base.day, ultimo_dia_mes)
    return date(anio, mes, dia)


def obtener_estado_turno(nombre_estado: str) -> Estado:
    """Busca un estado de tipo 'turno' (ej: 'pendiente', 'confirmado', 'cancelado')."""
    estado = Estado.objects.filter(
        tipo="turno",
        nombre__iexact=nombre_estado.strip(),
    ).first()
    if not estado:
        raise ValidationError(
            f"No existe un estado de tipo 'turno' llamado '{nombre_estado}' en el catálogo."
        )
    return estado


def validar_datos_contacto(nombre: str, apellido: str, telefono: str, email: str) -> dict:
    """Valida los 4 campos obligatorios sin espacios sobrantes ni formatos inválidos."""
    nombre_limpio = colapsar_espacios(nombre)
    apellido_limpio = colapsar_espacios(apellido)
    telefono_limpio = "".join((telefono or "").strip().split())
    email_limpio = "".join((email or "").strip().split()).lower()

    errores = {}

    if (
        not nombre_limpio
        or len(nombre_limpio) < 2
        or len(nombre_limpio) > 40
        or not RE_NOMBRE_APELLIDO.match(nombre_limpio)
    ):
        errores["nombre"] = "El nombre debe tener entre 2 y 40 letras (sin números ni espacios dobles)."

    if (
        not apellido_limpio
        or len(apellido_limpio) < 2
        or len(apellido_limpio) > 40
        or not RE_NOMBRE_APELLIDO.match(apellido_limpio)
    ):
        errores["apellido"] = "El apellido debe tener entre 2 y 40 letras (sin números ni espacios dobles)."

    if not telefono_limpio or not RE_TELEFONO.match(telefono_limpio):
        errores["telefono"] = "El teléfono solo puede contener números (6 a 15 dígitos), sin letras ni espacios."

    if (
        not email_limpio
        or len(email_limpio) > 100
        or email_limpio.startswith("@")
        or email_limpio.startswith(".")
        or not RE_EMAIL.match(email_limpio)
    ):
        errores["email"] = "Ingresá un correo válido (no puede empezar con @ ni tener espacios)."

    if errores:
        raise ValidationError(errores)

    return {
        "nombre": nombre_limpio,
        "apellido": apellido_limpio,
        "telefono": telefono_limpio,
        "email": email_limpio,
    }


def validar_fecha_y_bloque(fecha: date, hora: time) -> None:
    """Valida ventana de 1 mes desde hoy y bloques de 2 horas entre 09:00 y 19:00."""
    hoy = timezone.localdate()
    fecha_maxima = sumar_un_mes_calendario(hoy)

    if fecha < hoy:
        raise ValidationError("No se pueden reservar turnos en fechas pasadas.")

    if fecha > fecha_maxima:
        raise ValidationError(
            f"No se pueden reservar turnos con más de 1 mes de anticipación (máximo: {fecha_maxima.isoformat()})."
        )

    hora_normalizada = time(hora.hour, hora.minute)
    if hora_normalizada not in HORARIOS_DISPONIBLES:
        bloques_texto = ", ".join(h.strftime("%H:%M") for h in HORARIOS_DISPONIBLES)
        raise ValidationError(
            f"Horario inválido. Los turnos son en bloques de 2 horas de 09:00 a 19:00 (inicios permitidos: {bloques_texto})."
        )


def construir_mensaje_whatsapp(turno: Turno) -> dict:
    """Arma el resumen con los datos del turno para enviar y validar por WhatsApp."""
    hora_inicio = turno.hora
    hora_fin = time(
        (hora_inicio.hour + DURACION_BLOQUE_HORAS) % 24,
        hora_inicio.minute,
    )
    marca = (turno.vehiculo.marca or "").strip()
    modelo = (turno.vehiculo.modelo or "").strip()
    vehiculo_texto = marca if modelo.lower() in ("", "sin especificar", "none") else f"{marca} {modelo}".strip()

    mensaje = (
        f"Hola {turno.cliente.nombre}! Recibimos tu solicitud de turno en el lavadero:\n"
        f"- Cliente: {turno.cliente.nombre} {turno.cliente.apellido}\n"
        f"- Teléfono: {turno.cliente.telefono}\n"
        f"- Correo: {turno.cliente.email}\n"
        f"- Vehículo: {vehiculo_texto} ({turno.vehiculo.patente})\n"
        f"- Servicio: {turno.servicio.nombre_servicio}\n"
        f"- Fecha: {turno.fecha.strftime('%d/%m/%Y')}\n"
        f"- Horario (bloque de 2 hs): {hora_inicio.strftime('%H:%M')} a {hora_fin.strftime('%H:%M')}\n"
        f"- Estado actual: {turno.estado.nombre}\n"
        f"Respondé CONFIRMAR para validar tu turno."
    )
    telefono_digitos = "".join(ch for ch in (turno.cliente.telefono or "") if ch.isdigit())
    wa_url = f"https://wa.me/{telefono_digitos}?text={quote(mensaje)}" if telefono_digitos else ""

    return {
        "turno_id": turno.id_turno,
        "telefono": turno.cliente.telefono,
        "mensaje": mensaje,
        "whatsapp_url": wa_url,
        "estado": turno.estado.nombre,
    }


@transaction.atomic
def crear_turno(
    *,
    nombre: str,
    apellido: str,
    telefono: str,
    email: str,
    patente: str,
    servicio_id: int,
    fecha: date,
    hora: time,
    marca: str = "Sin especificar",
) -> dict:
    """
    Crea un turno en estado 'pendiente' validando datos obligatorios,
    ventana de 1 mes, bloque de 2 horas (09:00-19:00) y disponibilidad.
    Resuelve el vehículo por patente sin pedir ID manual ni campo modelo.
    """
    datos_contacto = validar_datos_contacto(nombre, apellido, telefono, email)
    validar_fecha_y_bloque(fecha, hora)

    patente_limpia = "".join((patente or "").strip().upper().split())
    if not RE_PATENTE.match(patente_limpia):
        raise ValidationError({"patente": "La patente debe tener entre 6 y 8 caracteres alfanuméricos sin espacios."})

    marca_limpia = colapsar_espacios(marca) or "Sin especificar"
    if len(marca_limpia) > 40 or not RE_MARCA.match(marca_limpia):
        raise ValidationError({"marca": "La marca debe tener hasta 40 caracteres sin espacios dobles."})

    hora_bloque = time(hora.hour, hora.minute)

    try:
        servicio = Servicio.objects.get(pk=servicio_id, activo=True)
    except Servicio.DoesNotExist:
        raise ValidationError("El servicio seleccionado no existe o está inactivo.")

    estado_pendiente = obtener_estado_turno("pendiente")
    estado_cancelado = Estado.objects.filter(tipo="turno", nombre__iexact="cancelado").first()

    turnos_dia = Turno.objects.select_for_update().filter(fecha=fecha, hora=hora_bloque)
    if estado_cancelado:
        turnos_dia = turnos_dia.exclude(estado=estado_cancelado)

    if turnos_dia.exists():
        hora_fin = time(hora_bloque.hour + DURACION_BLOQUE_HORAS, hora_bloque.minute)
        raise ValidationError(
            f"El bloque de {hora_bloque.strftime('%H:%M')} a {hora_fin.strftime('%H:%M')} "
            f"del {fecha.strftime('%d/%m/%Y')} ya se encuentra reservado."
        )

    vehiculo = Vehiculo.objects.select_related("cliente").filter(patente__iexact=patente_limpia).first()
    if vehiculo:
        cliente = vehiculo.cliente
        cliente.nombre = datos_contacto["nombre"]
        cliente.apellido = datos_contacto["apellido"]
        cliente.telefono = datos_contacto["telefono"]
        cliente.email = datos_contacto["email"]
        if hasattr(cliente, "activo"):
            cliente.activo = True
            cliente.save(update_fields=["nombre", "apellido", "telefono", "email", "activo"])
        else:
            cliente.save(update_fields=["nombre", "apellido", "telefono", "email"])

        vehiculo.marca = marca_limpia
        campos_vehiculo = ["marca"]
        if hasattr(vehiculo, "activo") and not vehiculo.activo:
            vehiculo.activo = True
            campos_vehiculo.append("activo")
        vehiculo.save(update_fields=campos_vehiculo)
    else:
        cliente_kwargs = {
            "nombre": datos_contacto["nombre"],
            "apellido": datos_contacto["apellido"],
            "telefono": datos_contacto["telefono"],
            "email": datos_contacto["email"],
        }
        if any(f.name == "activo" for f in Cliente._meta.fields):
            cliente_kwargs["activo"] = True
        cliente = Cliente.objects.create(**cliente_kwargs)

        vehiculo_kwargs = {
            "cliente": cliente,
            "patente": patente_limpia,
            "marca": marca_limpia,
        }
        if any(f.name == "modelo" for f in Vehiculo._meta.fields):
            vehiculo_kwargs["modelo"] = "Sin especificar"
        if any(f.name == "activo" for f in Vehiculo._meta.fields):
            vehiculo_kwargs["activo"] = True
        vehiculo = Vehiculo.objects.create(**vehiculo_kwargs)

    turno = Turno.objects.create(
        cliente=cliente,
        vehiculo=vehiculo,
        servicio=servicio,
        estado=estado_pendiente,
        fecha=fecha,
        hora=hora_bloque,
    )

    validacion_wh = construir_mensaje_whatsapp(turno)
    return {
        "turno": turno,
        "validacion_whatsapp": validacion_wh,
    }


@transaction.atomic
def confirmar_turno_desde_validacion(turno_id: int, aceptado_por_usuario: bool = True) -> Turno:
    """
    Cambia el turno de 'pendiente' a 'confirmado' SOLO si el usuario aceptó la validación.
    Si rechazó o no aceptó, lo pasa a 'cancelado'.
    """
    try:
        turno = Turno.objects.select_for_update().select_related("estado").get(pk=turno_id)
    except Turno.DoesNotExist:
        raise ValidationError("El turno indicado no existe.")

    if turno.estado.nombre.lower() == "cancelado":
        raise ValidationError("No se puede confirmar un turno que ya está cancelado.")

    if not aceptado_por_usuario:
        turno.estado = obtener_estado_turno("cancelado")
        turno.save(update_fields=["estado"])
        return turno

    turno.estado = obtener_estado_turno("confirmado")
    turno.save(update_fields=["estado"])
    return turno


@transaction.atomic
def cambiar_estado_turno(turno_id: int, nuevo_estado_nombre: str) -> Turno:
    """
    Permite cambiar entre pendiente, confirmado y cancelado,
    impidiendo pasar a 'confirmado' sin validación explícita si viene desde pendiente.
    """
    try:
        turno = Turno.objects.select_for_update().select_related("estado").get(pk=turno_id)
    except Turno.DoesNotExist:
        raise ValidationError("El turno indicado no existe.")

    estado_destino = obtener_estado_turno(nuevo_estado_nombre)
    estado_actual_nombre = turno.estado.nombre.lower()
    estado_destino_nombre = estado_destino.nombre.lower()

    if estado_actual_nombre == "pendiente" and estado_destino_nombre == "confirmado":
        raise ValidationError(
            "El turno está 'pendiente': solo puede pasar a 'confirmado' cuando el usuario acepte la validación."
        )

    if estado_destino_nombre in ("pendiente", "confirmado"):
        estado_cancelado = Estado.objects.filter(tipo="turno", nombre__iexact="cancelado").first()
        choque = Turno.objects.filter(fecha=turno.fecha, hora=turno.hora).exclude(pk=turno.pk)
        if estado_cancelado:
            choque = choque.exclude(estado=estado_cancelado)
        if choque.exists():
            raise ValidationError("Ya existe otro turno activo en esa fecha y bloque horario.")

    turno.estado = estado_destino
    turno.save(update_fields=["estado"])
    return turno