from django.db import models

class Estado(models.Model):
    tipo = models.CharField(max_length=50) # Ej: turno, orden, pago
    nombre = models.CharField(max_length=100) # Ej: Confirmado, Pendiente

    def __str__(self):
        return f"{self.tipo} - {self.nombre}"

class MedioPago(models.Model):
    nombre = models.CharField(max_length=100) # Ej: Efectivo, Transferencia

    def __str__(self):
        return self.nombre