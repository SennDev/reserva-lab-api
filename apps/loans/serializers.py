from rest_framework import serializers

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


class LoanStatusSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=Prestamo.ESTADO_CHOICES)

    def validate_estado(self, value):
        loan = self.context["loan"]
        transitions = {
            "Pendiente": {"Aprobado", "Rechazado"},
            "Aprobado": {"Devuelto", "Rechazado"},
            "Rechazado": set(),
            "Devuelto": set(),
        }

        if value == loan.estado:
            return value

        if value not in transitions.get(loan.estado, set()):
            raise serializers.ValidationError(
                f"No se puede cambiar de {loan.estado} a {value}."
            )

        return value
