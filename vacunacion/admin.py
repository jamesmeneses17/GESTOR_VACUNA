from django.contrib import admin
from .models import Propietario, Mascota, Especie, Vacuna, Veterinario, Cita, HistorialMedico, HistorialVacuna

admin.site.register(Propietario)
admin.site.register(Mascota)
admin.site.register(Especie)
admin.site.register(Vacuna)
admin.site.register(Veterinario)
admin.site.register(Cita)
admin.site.register(HistorialMedico)
admin.site.register(HistorialVacuna)
