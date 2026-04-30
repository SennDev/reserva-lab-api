from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "nombre_completo", "matricula", "rol", "tipo_usuario", "is_active")
    search_fields = ("email", "first_name", "last_name", "matricula")
    list_filter = ("rol", "tipo_usuario", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Información personal",
            {"fields": ("first_name", "last_name", "matricula", "carrera_departamento", "avatar_url")},
        ),
        ("Permisos", {"fields": ("rol", "tipo_usuario", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "matricula",
                    "carrera_departamento",
                    "tipo_usuario",
                    "rol",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

# Register your models here.
