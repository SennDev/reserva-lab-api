from rest_framework import serializers

from apps.labs.models import Laboratorio
from apps.reservations.models import Reserva
from apps.users.models import User


class ReservationSerializer(serializers.ModelSerializer):
    lab = serializers.SerializerMethodField()
    laboratorioId = serializers.SerializerMethodField()
    solicitante = serializers.SerializerMethodField()
    solicitanteId = serializers.SerializerMethodField()
    fecha = serializers.DateField(format="%d %b %Y", input_formats=["%Y-%m-%d"])
    fecha_iso = serializers.SerializerMethodField()
    laboratorio_ref = serializers.PrimaryKeyRelatedField(
        source="laboratorio",
        queryset=Laboratorio.objects.all(),
        write_only=True,
        required=False,
    )
    solicitante_ref = serializers.PrimaryKeyRelatedField(
        source="solicitante",
        queryset=User.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Reserva
        fields = (
            "id",
            "lab",
            "laboratorioId",
            "laboratorio_ref",
            "fecha",
            "fecha_iso",
            "horario",
            "materia",
            "motivo",
            "estado",
            "solicitante",
            "solicitanteId",
            "solicitante_ref",
        )
        read_only_fields = ("estado",)

    def to_internal_value(self, data):
        normalized = data.copy()
        if normalized.get("laboratorioId"):
            normalized["laboratorio_ref"] = normalized["laboratorioId"]
        if normalized.get("solicitanteId"):
            normalized["solicitante_ref"] = normalized["solicitanteId"]
        return super().to_internal_value(normalized)

    def get_lab(self, obj):
        return obj.laboratorio.nombre

    def get_laboratorioId(self, obj):
        return obj.laboratorio_id

    def get_solicitante(self, obj):
        return obj.solicitante.nombre_completo

    def get_solicitanteId(self, obj):
        return obj.solicitante_id

    def get_fecha_iso(self, obj):
        return obj.fecha.isoformat()


class ReservationStatusSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Reserva.ESTADO_CHOICES)

    def validate_estado(self, value):
        reservation = self.context["reservation"]
        transitions = {
            "Pendiente": {"Aprobada", "Rechazada"},
            "Aprobada": {"Completada", "Rechazada"},
            "Rechazada": set(),
            "Completada": set(),
        }

        if value == reservation.estado:
            return value

        if value not in transitions.get(reservation.estado, set()):
            raise serializers.ValidationError(
                f"No se puede cambiar de {reservation.estado} a {value}."
            )

        return value
