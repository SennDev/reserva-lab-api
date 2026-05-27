import re

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.users.models import User


def split_full_name(full_name: str) -> tuple[str, str]:
    parts = [part for part in full_name.strip().split() if part]
    if len(parts) < 2:
        return "", ""
    return parts[0], " ".join(parts[1:])


def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise serializers.ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError("La contraseña debe incluir al menos una mayúscula.")
    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError("La contraseña debe incluir al menos una minúscula.")
    if not re.search(r"\d", password):
        raise serializers.ValidationError("La contraseña debe incluir al menos un número.")


class UserSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="first_name", read_only=True)
    apellidos = serializers.CharField(source="last_name", read_only=True)
    nombre_completo = serializers.CharField(read_only=True)
    carrera = serializers.CharField(source="carrera_departamento", read_only=True)
    avatarUrl = serializers.URLField(source="avatar_url", read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            "id_usuario",
            "nombre",
            "apellidos",
            "nombre_completo",
            "matricula",
            "email",
            "carrera",
            "carrera_departamento",
            "tipo_usuario",
            "rol",
            "avatarUrl",
        )


class RegisterSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="first_name", required=False, write_only=True)
    apellidos = serializers.CharField(source="last_name", required=False, write_only=True)
    nombre_completo = serializers.CharField(required=False, write_only=True)
    carrera = serializers.CharField(required=False, write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    avatarUrl = serializers.URLField(source="avatar_url", required=False, allow_null=True, write_only=True)

    class Meta:
        model = User
        fields = (
            "id_usuario",
            "nombre",
            "apellidos",
            "nombre_completo",
            "matricula",
            "email",
            "carrera",
            "carrera_departamento",
            "tipo_usuario",
            "password",
            "confirm_password",
            "avatarUrl",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "carrera_departamento": {"required": False},
            "id_usuario": {"read_only": True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        full_name = attrs.pop("nombre_completo", "").strip()
        carrera = attrs.pop("carrera", "").strip()
        confirm_password = attrs.pop("confirm_password")
        password = attrs.get("password", "")

        if full_name and not attrs.get("first_name") and not attrs.get("last_name"):
            first_name, last_name = split_full_name(full_name)
            if first_name and last_name:
                attrs["first_name"] = first_name
                attrs["last_name"] = last_name

        if not attrs.get("first_name") or not attrs.get("last_name"):
            raise serializers.ValidationError(
                {"nombre_completo": "Debes proporcionar nombre y apellidos."}
            )

        if carrera and not attrs.get("carrera_departamento"):
            attrs["carrera_departamento"] = carrera

        if not attrs.get("carrera_departamento"):
            raise serializers.ValidationError(
                {"carrera_departamento": "Debes indicar tu carrera o departamento."}
            )

        validate_password_strength(password)
        validate_password(password)

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "La confirmación de contraseña no coincide."}
            )

        tipo_usuario = attrs.get("tipo_usuario", "estudiante")
        matricula = attrs.get("matricula", "")

        if tipo_usuario == "estudiante":
            if not re.fullmatch(r"\d{9}", matricula):
                raise serializers.ValidationError(
                    {"matricula": "La matrícula debe tener exactamente 9 dígitos."}
                )
            attrs["rol"] = "estudiante"
        elif tipo_usuario == "admin":
            attrs["rol"] = "admin"
        else:
            attrs["rol"] = "tecnico"

        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        return User.objects.create_user(password=password, **validated_data)


class CurrentUserUpdateSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(source="first_name", required=False)
    apellidos = serializers.CharField(source="last_name", required=False)
    carrera = serializers.CharField(source="carrera_departamento", required=False)
    avatarUrl = serializers.URLField(source="avatar_url", required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "nombre",
            "apellidos",
            "matricula",
            "email",
            "carrera",
            "carrera_departamento",
            "tipo_usuario",
            "avatarUrl",
        )


class ReservaLabTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.rol
        token["tipo_usuario"] = user.tipo_usuario
        token["nombre"] = user.nombre_completo
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
