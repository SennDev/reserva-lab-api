from rest_framework import serializers

from apps.equipment.models import Equipo
from apps.labs.models import Laboratorio


class EquipmentSerializer(serializers.ModelSerializer):
    laboratorio = serializers.SerializerMethodField()
    laboratorioId = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()
    laboratorio_ref = serializers.PrimaryKeyRelatedField(
        source="laboratorio",
        queryset=Laboratorio.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Equipo
        fields = (
            "id",
            "nombre",
            "numero_serie",
            "laboratorio",
            "laboratorioId",
            "laboratorio_ref",
            "ubicacion",
            "estado",
            "cantidad_total",
            "cantidad_disponible",
            "icon",
            "color",
        )
        extra_kwargs = {
            "ubicacion": {"required": False, "allow_blank": True},
            "cantidad_disponible": {"required": False},
        }

    def to_internal_value(self, data):
        normalized = data.copy()
        raw_lab_id = normalized.pop("laboratorioId", None)
        raw_location = normalized.get("laboratorio") or normalized.get("ubicacion")

        if raw_lab_id:
            normalized["laboratorio_ref"] = raw_lab_id

        if raw_location:
            possible_lab = Laboratorio.objects.filter(nombre__iexact=str(raw_location).strip()).first()
            if possible_lab and "laboratorio_ref" not in normalized:
                normalized["laboratorio_ref"] = possible_lab.pk
                normalized["ubicacion"] = possible_lab.nombre
            elif "ubicacion" not in normalized or not normalized.get("ubicacion"):
                normalized["ubicacion"] = str(raw_location).strip()

        return super().to_internal_value(normalized)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if "cantidad_disponible" not in attrs:
            attrs["cantidad_disponible"] = getattr(
                self.instance,
                "cantidad_disponible",
                attrs.get("cantidad_total", 1),
            )

        laboratorio = attrs.get("laboratorio", getattr(self.instance, "laboratorio", None))
        if laboratorio and not attrs.get("ubicacion"):
            attrs["ubicacion"] = laboratorio.nombre

        if not laboratorio and not attrs.get("ubicacion", "").strip():
            raise serializers.ValidationError(
                {"laboratorio": "Debes asignar el equipo a una ubicación."}
            )

        return attrs

    def get_laboratorio(self, obj):
        return obj.ubicacion

    def get_laboratorioId(self, obj):
        return obj.laboratorio_id

    def get_icon(self, obj):
        lower_name = obj.nombre.lower()
        if "router" in lower_name or "switch" in lower_name:
            return "bi-hdd-network"
        if "servidor" in lower_name:
            return "bi-server"
        if "arduino" in lower_name or "cpu" in lower_name:
            return "bi-cpu"
        if "impresora" in lower_name:
            return "bi-printer"
        if "osciloscopio" in lower_name:
            return "bi-activity"
        return "bi-tools"

    def get_color(self, obj):
        color_map = {
            "Disponible": "text-success",
            "En Préstamo": "text-primary",
            "Mantenimiento": "text-warning",
            "Baja": "text-danger",
        }
        return color_map.get(obj.estado, "text-muted")
