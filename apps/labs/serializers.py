from rest_framework import serializers

from apps.labs.models import Laboratorio


class LaboratorySerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    class Meta:
        model = Laboratorio
        fields = (
            "id",
            "nombre",
            "edificio",
            "tipo",
            "capacidad",
            "estado",
            "equipamiento",
            "icon",
            "color",
        )

    def to_internal_value(self, data):
        normalized = data.copy()
        equipamiento = normalized.get("equipamiento")
        if isinstance(equipamiento, str):
            normalized["equipamiento"] = [
                item.strip() for item in equipamiento.split(",") if item.strip()
            ]
        return super().to_internal_value(normalized)

    def get_icon(self, obj):
        icon_map = {
            "cómputo": "bi-pc-display",
            "computo": "bi-pc-display",
            "redes": "bi-hdd-network",
            "robótica": "bi-cpu",
            "robotica": "bi-cpu",
            "investigación": "bi-building-gear",
            "investigacion": "bi-building-gear",
        }
        lower_tipo = obj.tipo.lower()
        for keyword, icon in icon_map.items():
            if keyword in lower_tipo:
                return icon
        return "bi-building"

    def get_color(self, obj):
        color_map = {
            "Disponible": "text-success",
            "En Mantenimiento": "text-warning",
            "Ocupado": "text-danger",
        }
        return color_map.get(obj.estado, "text-primary")
