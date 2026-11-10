from django.db import models


class Estado(models.Model):
    TIPOS = [("turno", "Turno"), ("orden", "Orden"), ("pago", "Pago")]
    id_estado = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.tipo}: {self.nombre}"


class MedioPago(models.Model):
    id_medio_pago = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)

    def __str__(self):
        return self.nombre


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
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="convenios")
    condiciones = models.TextField()
    tipo_facturacion = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Convenio #{self.id_convenio}"


class Proveedor(models.Model):
    id_proveedor = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    ROLES = [("propietario", "Propietario"), ("gerente", "Gerente"),
    ("supervisor", "Supervisor"), ("lavador", "Lavador")]
    id_empleado = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rol = models.CharField(max_length=30, choices=ROLES)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


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
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="vehiculos")
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.patente


class Servicio(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_servicio = models.CharField(max_length=100)
    duracion = models.PositiveIntegerField(help_text="minutos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre_servicio


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="turnos")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT, related_name="turnos")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="turnos")
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="+")
    fecha = models.DateField()
    hora = models.TimeField()

    def __str__(self):
        return f"Turno #{self.id_turno} - {self.vehiculo.patente}"


class FichaTecnica(models.Model):
    id_ficha = models.AutoField(primary_key=True)
    turno = models.OneToOneField(Turno, on_delete=models.PROTECT, related_name="ficha_tecnica")
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name="fichas_tecnicas")
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
    ficha_tecnica = models.OneToOneField(FichaTecnica, on_delete=models.PROTECT, related_name="orden_trabajo")
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="+")
    hora_inicio = models.TimeField()

    def __str__(self):
        return f"Orden #{self.id_orden}"


class DetalleServicio(models.Model):
    id_detalle = models.AutoField(primary_key=True)
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.PROTECT, related_name="detalles_servicio")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT, related_name="detalles_servicio")
    empleado = models.ForeignKey(Empleado, on_delete=models.PROTECT, related_name="detalles_servicio")
    hora_fin = models.TimeField(null=True, blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle #{self.id_detalle} (Orden {self.orden_id})"


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


class ConsumoInsumo(models.Model):
    id_consumo = models.AutoField(primary_key=True)
    detalle = models.ForeignKey(DetalleServicio, on_delete=models.PROTECT, related_name="consumos")
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name="consumos")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Consumo #{self.id_consumo}"


class MovimientoStock(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name="movimientos")
    tipo_movimiento = models.CharField(max_length=30)  # entrada / salida
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField()
    motivo = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.tipo_movimiento} #{self.id_movimiento}"


class Compra(models.Model):
    id_compra = models.AutoField(primary_key=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, related_name="compras")
    fecha = models.DateTimeField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Compra #{self.id_compra}"


class DetalleCompra(models.Model):
    id_detalle_compra = models.AutoField(primary_key=True)
    compra = models.ForeignKey(Compra, on_delete=models.PROTECT, related_name="detalles")
    insumo = models.ForeignKey(Insumo, on_delete=models.PROTECT, related_name="detalles_compra")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Detalle compra #{self.id_detalle_compra}"

class Factura(models.Model):
    id_factura = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="facturas")
    convenio = models.ForeignKey(Convenio, on_delete=models.PROTECT, related_name="facturas", null=True, blank=True)
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.PROTECT, related_name="facturas")
    numero_factura = models.CharField(max_length=30, unique=True)
    fecha_emision = models.DateField()
    enviada_por_email = models.BooleanField(default=False)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.numero_factura


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True)
    factura = models.ForeignKey(Factura, on_delete=models.PROTECT, related_name="pagos")
    medio_pago = models.ForeignKey(MedioPago, on_delete=models.PROTECT, related_name="pagos")
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name="+")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_hora = models.DateTimeField()
    concepto = models.CharField(max_length=100, blank=True)
    pago_adelanto = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago #{self.id_pago}"
