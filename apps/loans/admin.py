from django.contrib import admin

from apps.loans.models import Prestamo


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ("id", "equipo", "solicitante", "fecha", "horario", "cantidad", "estado")
    search_fields = ("id", "equipo__nombre", "equipo__numero_serie", "solicitante__email")
    list_filter = ("estado", "fecha")

# Register your models here.
