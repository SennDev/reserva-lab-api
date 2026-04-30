from django.contrib import admin

from apps.labs.models import Laboratorio


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "tipo", "edificio", "capacidad", "estado")
    search_fields = ("id", "nombre", "tipo", "edificio")
    list_filter = ("estado", "tipo")

# Register your models here.
