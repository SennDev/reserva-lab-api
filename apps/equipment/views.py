from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrTecnicoRole, IsAdminRole
from apps.common.views import APIExceptionMixin
from apps.equipment.models import Equipo
from apps.equipment.serializers import EquipmentSerializer


class EquipmentViewSet(APIExceptionMixin, viewsets.ModelViewSet):
    queryset = Equipo.objects.select_related("laboratorio").all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    ordering_fields = ("nombre", "numero_serie", "cantidad_total", "cantidad_disponible")

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update"}:
            return [IsAdminOrTecnicoRole()]
        if self.action == "destroy":
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get("search")
        if search_term:
            queryset = queryset.filter(
                Q(nombre__icontains=search_term)
                | Q(numero_serie__icontains=search_term)
                | Q(ubicacion__icontains=search_term)
            )
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.estado == "En Préstamo":
            return Response(
                {"detail": "No puedes dar de baja un equipo actualmente prestado."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.estado = "Baja"
        instance.cantidad_disponible = 0
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Create your views here.
