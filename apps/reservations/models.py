from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.constants import HORARIOS_VALIDOS, RESERVA_ESTADOS_ACTIVOS
from apps.common.identifiers import generate_prefixed_code
from apps.labs.models import Laboratorio


class Reserva(models.Model):
    ESTADO_CHOICES = (
        ("Pendiente", "Pendiente"),
        ("Aprobada", "Aprobada"),
        ("Rechazada", "Rechazada"),
        ("Completada", "Completada"),
    )

    id = models.CharField(max_length=20, primary_key=True, editable=False)
    laboratorio = models.ForeignKey(
        Laboratorio,
        on_delete=models.PROTECT,
        related_name="reservas",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reservas",
    )
    fecha = models.DateField()
    horario = models.CharField(max_length=20)
    materia = models.CharField(max_length=200)
    motivo = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Pendiente")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("fecha", "horario", "laboratorio__nombre")

    def clean(self):
        errors = {}
        today = timezone.localdate()

        if self.fecha < today and self.estado in RESERVA_ESTADOS_ACTIVOS:
            errors["fecha"] = "No puedes realizar reservas en fechas que ya pasaron."

        if self.horario not in HORARIOS_VALIDOS:
            errors["horario"] = "Selecciona una franja horaria válida."

        if len((self.materia or "").strip()) < 4:
            errors["materia"] = "La materia debe tener al menos 4 caracteres."

        if len((self.motivo or "").strip()) < 10:
            errors["motivo"] = "El motivo debe tener al menos 10 caracteres."

        if self.laboratorio.estado != "Disponible" and self.estado in RESERVA_ESTADOS_ACTIVOS:
            errors["laboratorio"] = "El laboratorio seleccionado no está disponible para reservar."

        conflict_exists = (
            Reserva.objects.filter(
                laboratorio=self.laboratorio,
                fecha=self.fecha,
                horario=self.horario,
                estado__in=RESERVA_ESTADOS_ACTIVOS,
            )
            .exclude(pk=self.pk)
            .exists()
        )
        if conflict_exists and self.estado in RESERVA_ESTADOS_ACTIVOS:
            errors["horario"] = "Ya existe una reserva activa para ese laboratorio en ese horario."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_prefixed_code(Reserva, "RES")
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.id} - {self.laboratorio.nombre}"

# Create your models here.
