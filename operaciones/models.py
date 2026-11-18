from django.db import models

# Create your models here.

class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="turnos")
    vehiculo = models.ForeignKey("clientes.Vehiculo", on_delete=models.PROTECT, related_name="turnos")
    servicio = models.ForeignKey("catalogos.Servicio", on_delete=models.PROTECT, related_name="turnos")
    estado = models.ForeignKey("catalogos.Estado", on_delete=models.PROTECT, related_name="+")
    fecha = models.DateField()
    hora = models.TimeField()

    def __str__(self):
        return f"Turno #{self.id_turno} - {self.vehiculo.patente}"


class FichaTecnica(models.Model):
    id_ficha = models.AutoField(primary_key=True)
    turno = models.OneToOneField("Turno", on_delete=models.PROTECT, related_name="ficha_tecnica")
    empleado = models.ForeignKey("catalogos.Empleado", on_delete=models.PROTECT, related_name="fichas_tecnicas")
    fecha_hora_ingreso = models.DateTimeField()
    estado_pintura = models.CharField(max_length=100)
    estado_vidrios = models.CharField(max_length=100)
    estado_opticas = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True)
    danos_preexistentes = models.TextField(blank=True)
    confirmada = models.BooleanField(default=False)

    def __str__(self):
        return f"Ficha #{self.id_ficha}"


class OrdenTrabajo(models.Model):
    id_orden = models.AutoField(primary_key=True)
    ficha_tecnica = models.OneToOneField("FichaTecnica", on_delete=models.PROTECT, related_name="orden_trabajo")
    estado = models.ForeignKey("catalogos.Estado", on_delete=models.PROTECT, related_name="+")
    hora_inicio = models.TimeField()

    def __str__(self):
        return f"Orden #{self.id_orden}"


class DetalleServicio(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    orden = models.ForeignKey("OrdenTrabajo", on_delete=models.PROTECT, related_name="detalles_servicio")
    servicio = models.ForeignKey("catalogos.Servicio", on_delete=models.PROTECT, related_name="detalles_servicio")
    empleado = models.ForeignKey("catalogos.Empleado", on_delete=models.PROTECT, related_name="detalles_servicio")
    hora_fin = models.TimeField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle #{self.id_detalle} (Orden {self.orden_id})"

class ConsumoInsumo(models.Model):
    id_consumo = models.AutoField(primary_key=True)
    detalle = models.ForeignKey("DetalleServicio", on_delete=models.PROTECT, related_name="consumos")
    insumo = models.ForeignKey("insumos.Insumo", on_delete=models.PROTECT, related_name="consumos")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Consumo #{self.id_consumo}"