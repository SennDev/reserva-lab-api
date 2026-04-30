from django.core.exceptions import ValidationError
from django.db import models

from apps.common.identifiers import generate_prefixed_code


class Laboratorio(models.Model):
    ESTADO_CHOICES = (
        ("Disponible", "Disponible"),
        ("En Mantenimiento", "En Mantenimiento"),
        ("Ocupado", "Ocupado"),
    )

    id = models.CharField(max_length=20, primary_key=True, editable=False)
    nombre = models.CharField(max_length=200, unique=True)
    edificio = models.CharField(max_length=100)
    tipo = models.CharField(max_length=80)
    capacidad = models.PositiveSmallIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Disponible")
    equipamiento = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ("nombre",)

    def clean(self):
        errors = {}

        if len((self.nombre or "").strip()) < 5:
            errors["nombre"] = "El nombre debe tener al menos 5 caracteres."

        if len((self.edificio or "").strip()) < 2:
            errors["edificio"] = "Ingresa un edificio o ubicación válida."

        if len((self.tipo or "").strip()) < 3:
            errors["tipo"] = "Indica un tipo de laboratorio válido."

        if not 1 <= int(self.capacidad or 0) <= 100:
            errors["capacidad"] = "La capacidad debe estar entre 1 y 100."

        if not isinstance(self.equipamiento, list):
            errors["equipamiento"] = "El equipamiento debe enviarse como lista."
        else:
            cleaned = [item.strip() for item in self.equipamiento if str(item).strip()]
            if not cleaned:
                errors["equipamiento"] = "Debes detallar al menos un equipo principal."
            self.equipamiento = cleaned

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_prefixed_code(Laboratorio, "LAB")
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.nombre

# Create your models here.
