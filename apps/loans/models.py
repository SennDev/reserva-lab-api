from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.common.constants import HORARIOS_VALIDOS, PRESTAMO_ESTADOS_ACTIVOS
from apps.common.identifiers import generate_prefixed_code
from apps.common.time_slots import time_slots_overlap
from apps.equipment.models import Equipo


class Prestamo(models.Model):
    ESTADO_CHOICES = (
        ("Pendiente", "Pendiente"),
        ("Aprobado", "Aprobado"),
        ("Rechazado", "Rechazado"),
        ("Devuelto", "Devuelto"),
    )

    id = models.CharField(max_length=20, primary_key=True, editable=False)
    equipo = models.ForeignKey(
        Equipo,
        on_delete=models.PROTECT,
        related_name="prestamos",
    )
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="prestamos",
    )
    fecha = models.DateField()
    horario = models.CharField(max_length=20)
    proyecto = models.CharField(max_length=200)
    motivo = models.TextField()
    cantidad = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Pendiente")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("fecha", "horario", "equipo__nombre")

    def clean(self):
        errors = {}
        today = timezone.localdate()

        if self.fecha < today and self.estado in PRESTAMO_ESTADOS_ACTIVOS:
            errors["fecha"] = "No puedes solicitar préstamos en fechas que ya pasaron."

        if self.horario not in HORARIOS_VALIDOS:
            errors["horario"] = "Selecciona una franja horaria válida."

        if len((self.proyecto or "").strip()) < 4:
            errors["proyecto"] = "El proyecto o materia debe tener al menos 4 caracteres."

        if len((self.motivo or "").strip()) < 10:
            errors["motivo"] = "El motivo debe tener al menos 10 caracteres."

        if int(self.cantidad or 0) <= 0:
            errors["cantidad"] = "La cantidad solicitada debe ser mayor a 0."

        if int(self.cantidad or 0) > int(self.equipo.cantidad_total or 0):
            errors["cantidad"] = "La cantidad solicitada no puede superar el inventario total."

        approved_loans = Prestamo.objects.filter(
            equipo=self.equipo,
            fecha=self.fecha,
            estado="Aprobado",
        ).exclude(pk=self.pk)

        conflict_exists = any(time_slots_overlap(self.horario, loan.horario) for loan in approved_loans)
        if conflict_exists and self.estado in PRESTAMO_ESTADOS_ACTIVOS:
            errors["horario"] = "Este horario ya está reservado para el equipo seleccionado."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_prefixed_code(Prestamo, "PR")
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.id} - {self.equipo.nombre}"

# Create your models here.
