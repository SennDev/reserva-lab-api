from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.equipment.models import Equipo
from apps.labs.models import Laboratorio
from apps.loans.models import Prestamo
from apps.reservations.models import Reserva
from apps.users.models import User


class DashboardApiTests(APITestCase):
    def test_summary_returns_expected_shape(self):
        user = User.objects.create_user(
            email="student@alumno.buap.mx",
            password="Student123",
            first_name="Ana",
            last_name="Martinez",
            matricula="202300020",
            carrera_departamento="Ciencias de la Computación",
            tipo_usuario="estudiante",
            rol="estudiante",
        )
        lab = Laboratorio.objects.create(
            nombre="Laboratorio de Integración",
            edificio="CCO1",
            tipo="Cómputo",
            capacidad=30,
            estado="Disponible",
            equipamiento=["PCs", "Pantallas"],
        )
        equipment = Equipo.objects.create(
            nombre="Kit Arduino Mega 2560",
            numero_serie="SN-ARD-7788",
            ubicacion="Almacén Central",
            estado="Disponible",
            cantidad_total=8,
            cantidad_disponible=8,
        )
        Reserva.objects.create(
            laboratorio=lab,
            solicitante=user,
            fecha=timezone.localdate() + timedelta(days=1),
            horario="11:00 - 13:00",
            materia="Desarrollo Web",
            motivo="Reserva de laboratorio para trabajo integrador.",
            estado="Aprobada",
        )
        Prestamo.objects.create(
            equipo=equipment,
            solicitante=user,
            fecha=timezone.localdate() + timedelta(days=1),
            horario="15:00 - 17:00",
            proyecto="Embebidos",
            motivo="Préstamo para prototipo de sensores y actuadores.",
            cantidad=1,
            estado="Pendiente",
        )

        self.client.force_authenticate(user)
        response = self.client.get("/api/dashboard/summary/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("stats", response.data)
        self.assertIn("proximas_reservas", response.data)
        self.assertIn("ocupacion_global", response.data)
        self.assertEqual(len(response.data["stats"]), 3)

# Create your tests here.
