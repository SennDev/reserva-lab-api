from django.core.exceptions import ValidationError
from django.db import models

from apps.common.identifiers import generate_prefixed_code
from apps.labs.models import Laboratorio


class Equipo(models.Model):
    ESTADO_CHOICES = (
        ("Disponible", "Disponible"),
        ("En Préstamo", "En Préstamo"),
        ("Mantenimiento", "Mantenimiento"),
        ("Baja", "Baja"),
    )

    id = models.CharField(max_length=20, primary_key=True, editable=False)
    nombre = models.CharField(max_length=200)
    numero_serie = models.CharField(max_length=100, unique=True)
    laboratorio = models.ForeignKey(
        Laboratorio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipos",
    )
    ubicacion = models.CharField(max_length=200, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Disponible")
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disponible = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ("nombre", "numero_serie")

    def clean(self):
        errors = {}

        if len((self.nombre or "").strip()) < 5:
            errors["nombre"] = "El nombre del equipo debe tener al menos 5 caracteres."

        if len((self.numero_serie or "").strip()) < 4:
            errors["numero_serie"] = "Ingresa un número de serie válido."

        if self.laboratorio and not self.ubicacion:
            self.ubicacion = self.laboratorio.nombre

        if not (self.laboratorio or (self.ubicacion or "").strip()):
            errors["laboratorio"] = "Debes asignar el equipo a una ubicación."

        if int(self.cantidad_total or 0) <= 0:
            errors["cantidad_total"] = "La cantidad total debe ser mayor a 0."

        if int(self.cantidad_disponible or 0) < 0:
            errors["cantidad_disponible"] = "La cantidad disponible no puede ser negativa."

        if int(self.cantidad_disponible or 0) > int(self.cantidad_total or 0):
            errors["cantidad_disponible"] = "La cantidad disponible no puede superar la cantidad total."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_prefixed_code(Equipo, "EQ")
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.nombre} ({self.numero_serie})"

# Create your models here.
