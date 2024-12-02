from django.db import models
from django.utils import timezone

class Propietario(models.Model):
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=45)
    cedula = models.IntegerField(unique=True)
    direccion = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=45, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Especie(models.Model):
    nombre = models.CharField(max_length=45)

    def __str__(self):
        return self.nombre

class Mascota(models.Model):
    nombre = models.CharField(max_length=45)
    especie = models.ForeignKey('Especie', on_delete=models.RESTRICT)
    raza = models.CharField(max_length=45, blank=True, null=True)
    fecha_nacimiento = models.DateField()
    propietario = models.ForeignKey('Propietario', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Veterinario(models.Model):
    nombre = models.CharField(max_length=45)
    apellido = models.CharField(max_length=45)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(max_length=45, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Vacuna(models.Model):
    nombre = models.CharField(max_length=45)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre

class Cita(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    veterinario = models.ForeignKey(Veterinario, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    motivo = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cita para {self.mascota.nombre} con {self.veterinario.nombre} el {self.fecha_hora}"

class HistorialMedico(models.Model):
    cita = models.ForeignKey(Cita, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)

class HistorialVacuna(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE, related_name='historial_vacunas')  # Relación con Mascota
    vacuna = models.ForeignKey('Vacuna', on_delete=models.CASCADE)
    fecha_aplicacion = models.DateField()
    estado = models.CharField(max_length=20, choices=[('pendiente', 'Pendiente'), ('administrada', 'Administrada'), ('no administrada', 'No Administrada')])
    fecha_proxima = models.DateField(blank=True, null=True)  # Campo agregado para la próxima fecha de vacunación
    notas = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.vacuna.nombre} - {self.estado}"

    def dias_hasta_proxima(self):
        if self.fecha_proxima:
            return (self.fecha_proxima - timezone.now().date()).days
        return None

class Vacunacion(models.Model):
    mascota = models.ForeignKey(Mascota, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    fecha_vacunacion = models.DateField()

    def __str__(self):
        return f'{self.nombre} ({self.fecha_vacunacion})'
