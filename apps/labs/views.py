from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import IsAdminRole
from apps.common.views import APIExceptionMixin
from apps.labs.models import Laboratorio
from apps.labs.serializers import LaboratorySerializer


class LaboratoryViewSet(APIExceptionMixin, viewsets.ModelViewSet):
    queryset = Laboratorio.objects.all()
    serializer_class = LaboratorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None
    ordering_fields = ("nombre", "tipo", "capacidad", "edificio")

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsAdminRole()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_term = self.request.query_params.get("search")
        if search_term:
            queryset = queryset.filter(
                Q(nombre__icontains=search_term)
                | Q(edificio__icontains=search_term)
                | Q(tipo__icontains=search_term)
                | Q(equipamiento__icontains=search_term)
            )
        return queryset

    @action(detail=False, methods=["get"], url_path="disponibles")
    def disponibles(self, request):
        serializer = self.get_serializer(
            self.get_queryset().filter(estado="Disponible"),
            many=True,
        )
        return Response(serializer.data)

# Create your views here.
