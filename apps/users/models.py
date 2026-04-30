import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.users.managers import UserManager


class User(AbstractUser):
    TIPO_CHOICES = (
        ("estudiante", "Estudiante"),
        ("personal", "Personal"),
    )
    ROL_CHOICES = (
        ("admin", "Admin"),
        ("tecnico", "Técnico"),
        ("estudiante", "Estudiante"),
    )

    username = None
    id_usuario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    matricula = models.CharField(max_length=20, unique=True)
    carrera_departamento = models.CharField(max_length=150)
    avatar_url = models.URLField(blank=True, null=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES, default="estudiante")
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default="estudiante")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "matricula"]

    objects = UserManager()

    class Meta:
        ordering = ("first_name", "last_name", "email")

    @property
    def nombre_completo(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def save(self, *args, **kwargs):
        if self.rol in {"admin", "tecnico"}:
            self.is_staff = True
        elif not self.is_superuser:
            self.is_staff = False
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.nombre_completo or self.email} ({self.rol})"

# Create your models here.
