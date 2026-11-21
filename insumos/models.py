from django.db import models

# Create your models here.

class Insumo(models.Model):
    id_insumo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    unidad_medida = models.CharField(max_length=30)
    stock_actual = models.DecimalField(max_digits=10, decimal_places=2)
    stock_minimo = models.DecimalField(max_digits=10, decimal_places=2)
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


class MovimientoStock(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    insumo = models.ForeignKey("insumos.Insumo", on_delete=models.PROTECT, related_name="movimientos")
    tipo_movimiento = models.CharField(max_length=30)  # entrada / salida
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField()
    motivo = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.tipo_movimiento} #{self.id_movimiento}"


class Compra(models.Model):
    id_compra = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey("insumos.Proveedor", on_delete=models.PROTECT, related_name="compras")
    fecha = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra #{self.id_compra}"


class DetalleCompra(models.Model):
    id_detalle_compra = models.AutoField(primary_key=True)
    compra = models.ForeignKey("insumos.Compra", on_delete=models.PROTECT, related_name="detalles")
    insumo = models.ForeignKey("insumos.Insumo", on_delete=models.PROTECT, related_name="detalles_compra")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle compra #{self.id_detalle_compra}"

class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.nombre