from rest_framework import serializers

from apps.common.time_slots import time_slots_overlap
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

    def validate(self, attrs):
        attrs = super().validate(attrs)
        laboratorio = attrs.get("laboratorio") or getattr(self.instance, "laboratorio", None)
        fecha = attrs.get("fecha") or getattr(self.instance, "fecha", None)
        horario = attrs.get("horario") or getattr(self.instance, "horario", None)

        if laboratorio and fecha and horario:
            self._validate_approved_overlap(laboratorio, fecha, horario, self.instance)

        return attrs

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

    @staticmethod
    def _validate_approved_overlap(laboratorio, fecha, horario, instance=None):
        approved_reservations = Reserva.objects.filter(
            laboratorio=laboratorio,
            fecha=fecha,
            estado="Aprobada",
        )

        if instance:
            approved_reservations = approved_reservations.exclude(pk=instance.pk)

        if any(time_slots_overlap(horario, reservation.horario) for reservation in approved_reservations):
            raise serializers.ValidationError(
                {"horario": "Este horario ya está reservado para el laboratorio seleccionado."}
            )


class ReservationStatusSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Reserva.ESTADO_CHOICES)

    def validate_estado(self, value):
        reservation = self.context["reservation"]
        request = self.context.get("request")
        transitions = {
            "Pendiente": {"Aprobada", "Rechazada"},
            "Aprobada": {"Completada", "Rechazada"},
            "Rechazada": set(),
            "Completada": set(),
        }

        if not request or request.user.rol not in {"admin", "tecnico"}:
            raise serializers.ValidationError("Solo administradores y técnicos pueden cambiar estados.")

        if value == reservation.estado:
            return value

        if value not in transitions.get(reservation.estado, set()):
            raise serializers.ValidationError(
                f"No se puede cambiar de {reservation.estado} a {value}."
            )

        if value == "Aprobada":
            ReservationSerializer._validate_approved_overlap(
                reservation.laboratorio,
                reservation.fecha,
                reservation.horario,
                reservation,
            )

        return value
