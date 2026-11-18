from django.db import models

# Create your models here.

class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.PROTECT, related_name="facturas")
    convenio = models.ForeignKey("clientes.Convenio", on_delete=models.PROTECT, related_name="facturas", null=True, blank=True)
    orden = models.ForeignKey("operaciones.OrdenTrabajo", on_delete=models.PROTECT, related_name="facturas")
    numero_factura = models.CharField(max_length=30, unique=True)
    fecha_emision = models.DateField()
    enviada_por_email = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.numero_factura


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    factura = models.ForeignKey("finanzas.Factura", on_delete=models.PROTECT, related_name="pagos")
    medio_pago = models.ForeignKey("catalogos.MedioPago", on_delete=models.PROTECT, related_name="pagos")
    estado = models.ForeignKey("catalogos.Estado", on_delete=models.PROTECT, related_name="+")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField()
    concepto = models.CharField(max_length=100, blank=True)
    pago_adelanto = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago #{self.id_pago}"