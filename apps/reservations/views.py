from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminOrTecnicoRole, IsOwnerOrStaffRole
from apps.common.views import APIExceptionMixin
from apps.reservations.models import Reserva
from apps.reservations.serializers import ReservationSerializer, ReservationStatusSerializer


class ReservationViewSet(APIExceptionMixin, viewsets.ModelViewSet):
    queryset = Reserva.objects.select_related("laboratorio", "solicitante").all()
    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    filterset_fields = ("estado", "fecha")
    ordering_fields = ("fecha", "created_at", "materia")

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
                Q(laboratorio__nombre__icontains=search_term)
                | Q(materia__icontains=search_term)
                | Q(estado__icontains=search_term)
            )

        if self.request.query_params.get("solicitanteId"):
            queryset = queryset.filter(solicitante_id=self.request.query_params["solicitanteId"])

        if self.request.query_params.get("laboratorioId"):
            queryset = queryset.filter(laboratorio_id=self.request.query_params["laboratorioId"])

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if user.rol == "tecnico":
            raise PermissionError("Los técnicos no pueden crear reservas desde esta API.")

        requested_user = serializer.validated_data.pop("solicitante", None)
        owner = requested_user if user.rol == "admin" and requested_user else user
        serializer.save(solicitante=owner)

    @action(detail=True, methods=["patch"], url_path="estado")
    def estado(self, request, pk=None):
        reservation = self.get_object()
        serializer = ReservationStatusSerializer(
            data=request.data,
            context={"reservation": reservation, "request": request},
        )
        serializer.is_valid(raise_exception=True)
        reservation.estado = serializer.validated_data["estado"]
        reservation.save()
        return Response(ReservationSerializer(reservation).data)

# Create your views here.
