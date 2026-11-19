from django.db import models


class Estado(models.Model):
    TIPOS = [("turno", "Turno"), ("orden", "Orden"), ("pago", "Pago")]
    id_estado = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    nombre = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tipo}: {self.nombre}"


class MedioPago(models.Model):
    id_medio_pago = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    ROLES = [
        ("propietario", "Propietario"),
        ("gerente", "Gerente"),
        ("supervisor", "Supervisor"),
        ("lavador", "Lavador"),
    ]
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rol = models.CharField(max_length=30, choices=ROLES)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_servicio = models.CharField(max_length=100)
    duracion = models.PositiveIntegerField(help_text="minutos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_servicio