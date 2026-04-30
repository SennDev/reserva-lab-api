from django.db.models import Count, Q
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.labs.models import Laboratorio
from apps.loans.models import Prestamo
from apps.reservations.models import Reserva


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()

        my_reservations = Reserva.objects.filter(solicitante=user)
        my_future_reservations = my_reservations.filter(
            fecha__gte=today,
            estado__in=["Pendiente", "Aprobada"],
        )
        my_loans = Prestamo.objects.filter(solicitante=user)
        active_loans = my_loans.filter(estado__in=["Pendiente", "Aprobado"])

        total_labs = Laboratorio.objects.count()
        today_reserved_labs = (
            Reserva.objects.filter(fecha=today, estado__in=["Pendiente", "Aprobada"])
            .values("laboratorio")
            .distinct()
            .count()
        )
        ocupacion_global = round((today_reserved_labs / total_labs) * 100) if total_labs else 0

        next_reservations = list(
            my_future_reservations.select_related("laboratorio")
            .order_by("fecha", "horario")[:3]
        )

        stats = [
            {
                "title": "Mis Reservas Activas",
                "value": my_future_reservations.count(),
                "subtext": f"{my_reservations.filter(fecha=today).count()} programadas para hoy",
                "icon": "bi-calendar2-check-fill",
                "color": "text-primary",
            },
            {
                "title": "Préstamos Pendientes",
                "value": active_loans.count(),
                "subtext": active_loans.first().equipo.nombre if active_loans.exists() else "Sin préstamos activos",
                "icon": "bi-tools",
                "color": "text-warning",
            },
            {
                "title": "Labs Disponibles",
                "value": Laboratorio.objects.filter(estado="Disponible").count(),
                "subtext": f"De {total_labs} espacios totales",
                "icon": "bi-building-check",
                "color": "text-success",
            },
        ]

        proximas_reservas = [
            {
                "lab": reservation.laboratorio.nombre,
                "materia": reservation.materia,
                "fecha": f"{reservation.fecha.strftime('%d %b %Y')}, {reservation.horario}",
                "estado": "Confirmada" if reservation.estado == "Aprobada" else reservation.estado,
                "badgeClass": "badge-success-neo"
                if reservation.estado == "Aprobada"
                else "badge-warning-neo",
            }
            for reservation in next_reservations
        ]

        return Response(
            {
                "stats": stats,
                "proximas_reservas": proximas_reservas,
                "ocupacion_global": ocupacion_global,
            }
        )

# Create your views here.
