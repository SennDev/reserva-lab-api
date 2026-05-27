from django.db import transaction
from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrTecnicoRole, IsOwnerOrStaffRole
from apps.common.views import APIExceptionMixin
from apps.loans.models import Prestamo
from apps.loans.serializers import LoanSerializer, LoanStatusSerializer


class LoanViewSet(APIExceptionMixin, viewsets.ModelViewSet):
    queryset = Prestamo.objects.select_related("equipo", "solicitante").all()
    serializer_class = LoanSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_fields = ("estado", "fecha")
    ordering_fields = ("fecha", "created_at", "cantidad")

    def get_permissions(self):
        if self.action == "estado":
            return [IsAdminOrTecnicoRole()]
        if self.action in {"retrieve", "destroy"}:
            return [IsAuthenticated(), IsOwnerOrStaffRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.rol == "estudiante":
            queryset = queryset.filter(solicitante=user)

        search_term = self.request.query_params.get("search")
        if search_term:
            queryset = queryset.filter(
                Q(equipo__nombre__icontains=search_term)
                | Q(equipo__numero_serie__icontains=search_term)
                | Q(estado__icontains=search_term)
            )

        if self.request.query_params.get("solicitanteId"):
            queryset = queryset.filter(solicitante_id=self.request.query_params["solicitanteId"])

        if self.request.query_params.get("equipoId"):
            queryset = queryset.filter(equipo_id=self.request.query_params["equipoId"])

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if user.rol == "tecnico":
            raise PermissionError("Los técnicos no pueden crear préstamos desde esta API.")

        requested_user = serializer.validated_data.pop("solicitante", None)
        owner = requested_user if user.rol == "admin" and requested_user else user
        serializer.save(solicitante=owner)

    @action(detail=True, methods=["patch"], url_path="estado")
    def estado(self, request, pk=None):
        loan = self.get_object()
        serializer = LoanStatusSerializer(data=request.data, context={"loan": loan, "request": request})
        serializer.is_valid(raise_exception=True)
        new_state = serializer.validated_data["estado"]

        with transaction.atomic():
            equipment = loan.equipo
            previous_state = loan.estado

            if previous_state != new_state:
                if previous_state != "Aprobado" and new_state == "Aprobado":
                    if loan.cantidad > equipment.cantidad_disponible:
                        return Response(
                            {"detail": "No hay suficiente inventario disponible para aprobar el préstamo."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    equipment.cantidad_disponible -= loan.cantidad
                elif previous_state == "Aprobado" and new_state in {"Rechazado", "Devuelto"}:
                    equipment.cantidad_disponible += loan.cantidad

                if equipment.estado not in {"Mantenimiento", "Baja"}:
                    if equipment.cantidad_disponible == equipment.cantidad_total:
                        equipment.estado = "Disponible"
                    else:
                        equipment.estado = "En Préstamo"

                equipment.save()
                loan.estado = new_state
                loan.save()

        return Response(LoanSerializer(loan).data)

# Create your views here.
