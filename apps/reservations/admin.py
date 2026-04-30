from django.contrib import admin

from apps.reservations.models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("id", "laboratorio", "solicitante", "fecha", "horario", "estado")
    search_fields = ("id", "laboratorio__nombre", "solicitante__email", "materia")
    list_filter = ("estado", "fecha")

# Register your models here.
