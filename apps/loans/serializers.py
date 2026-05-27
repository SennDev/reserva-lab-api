from rest_framework import serializers

from apps.common.time_slots import time_slots_overlap
from apps.equipment.models import Equipo
from apps.loans.models import Prestamo
from apps.users.models import User


class LoanSerializer(serializers.ModelSerializer):
    equipo = serializers.SerializerMethodField()
    equipoId = serializers.SerializerMethodField()
    numero_serie = serializers.SerializerMethodField()
    solicitante = serializers.SerializerMethodField()
    solicitanteId = serializers.SerializerMethodField()
    fecha = serializers.DateField(format="%d %b %Y", input_formats=["%Y-%m-%d"])
    fecha_iso = serializers.SerializerMethodField()
    equipo_ref = serializers.PrimaryKeyRelatedField(
        source="equipo",
        queryset=Equipo.objects.all(),
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
        model = Prestamo
        fields = (
            "id",
            "equipo",
            "equipoId",
            "equipo_ref",
            "numero_serie",
            "fecha",
            "fecha_iso",
            "horario",
            "proyecto",
            "motivo",
            "cantidad",
            "estado",
            "solicitante",
            "solicitanteId",
            "solicitante_ref",
        )
        read_only_fields = ("estado",)

    def to_internal_value(self, data):
        normalized = data.copy()
        if normalized.get("equipoId"):
            normalized["equipo_ref"] = normalized["equipoId"]
        if normalized.get("solicitanteId"):
            normalized["solicitante_ref"] = normalized["solicitanteId"]
        return super().to_internal_value(normalized)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        equipo = attrs.get("equipo") or getattr(self.instance, "equipo", None)
        fecha = attrs.get("fecha") or getattr(self.instance, "fecha", None)
        horario = attrs.get("horario") or getattr(self.instance, "horario", None)

        if equipo and fecha and horario:
            self._validate_approved_overlap(equipo, fecha, horario, self.instance)

        return attrs

    def get_equipo(self, obj):
        return obj.equipo.nombre

    def get_equipoId(self, obj):
        return obj.equipo_id

    def get_numero_serie(self, obj):
        return obj.equipo.numero_serie

    def get_solicitante(self, obj):
        return obj.solicitante.nombre_completo

    def get_solicitanteId(self, obj):
        return obj.solicitante_id

    def get_fecha_iso(self, obj):
        return obj.fecha.isoformat()

    @staticmethod
    def _validate_approved_overlap(equipo, fecha, horario, instance=None):
        approved_loans = Prestamo.objects.filter(
            equipo=equipo,
            fecha=fecha,
            estado="Aprobado",
        )

        if instance:
            approved_loans = approved_loans.exclude(pk=instance.pk)

        if any(time_slots_overlap(horario, loan.horario) for loan in approved_loans):
            raise serializers.ValidationError(
                {"horario": "Este horario ya está reservado para el equipo seleccionado."}
            )


class LoanStatusSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Prestamo.ESTADO_CHOICES)

    def validate_estado(self, value):
        loan = self.context["loan"]
        request = self.context.get("request")
        transitions = {
            "Pendiente": {"Aprobado", "Rechazado"},
            "Aprobado": {"Devuelto", "Rechazado"},
            "Rechazado": set(),
            "Devuelto": set(),
        }

        if not request or request.user.rol not in {"admin", "tecnico"}:
            raise serializers.ValidationError("Solo administradores y técnicos pueden cambiar estados.")

        if value == loan.estado:
            return value

        if value not in transitions.get(loan.estado, set()):
            raise serializers.ValidationError(
                f"No se puede cambiar de {loan.estado} a {value}."
            )

        if value == "Aprobado":
            LoanSerializer._validate_approved_overlap(
                loan.equipo,
                loan.fecha,
                loan.horario,
                loan,
            )

        return value
