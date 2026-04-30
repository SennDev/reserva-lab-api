from django.contrib import admin

from apps.equipment.models import Equipo


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "numero_serie",
        "ubicacion",
        "estado",
        "cantidad_total",
        "cantidad_disponible",
    )
    search_fields = ("id", "nombre", "numero_serie", "ubicacion")
    list_filter = ("estado",)

# Register your models here.
