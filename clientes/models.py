from django.db import models

# Create your models here.
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, blank=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Vehiculo(models.Model):
    id_vehiculo = models.AutoField(primary_key=True)
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="vehiculos")
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.patente

class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    razon_social = models.CharField(max_length=100)
    cuit = models.CharField(max_length=13)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.razon_social


class Convenio(models.Model):
    id_convenio = models.AutoField(primary_key=True)
    empresa = models.ForeignKey("clientes.Empresa", on_delete=models.PROTECT, related_name="convenios")
    condiciones = models.TextField()
    tipo_facturacion = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Convenio #{self.id_convenio}"