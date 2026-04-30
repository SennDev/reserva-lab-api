from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.equipment.models import Equipo
from apps.labs.models import Laboratorio
from apps.loans.models import Prestamo
from apps.users.models import User


class LoanApiTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="student@alumno.buap.mx",
            password="Student123",
            first_name="Pablo",
            last_name="Ibarra",
            matricula="202300010",
            carrera_departamento="Ciencias de la Computación",
            tipo_usuario="estudiante",
            rol="estudiante",
        )
        self.tecnico = User.objects.create_user(
            email="tecnico@reservalab.local",
            password="Tecnico1234",
            first_name="Dulce",
            last_name="Aranza",
            matricula="EMP000010",
            carrera_departamento="Laboratorios",
            tipo_usuario="personal",
            rol="tecnico",
        )
        self.lab = Laboratorio.objects.create(
            nombre="Laboratorio de Hardware Especializado",
            edificio="CCO3",
            tipo="Robótica",
            capacidad=18,
            estado="Disponible",
            equipamiento=["Osciloscopios", "Kits Arduino"],
        )
        self.equipment = Equipo.objects.create(
            nombre="Osciloscopio Digital Rigol",
            numero_serie="SN-RIG-9001",
            laboratorio=self.lab,
            ubicacion=self.lab.nombre,
            estado="Disponible",
            cantidad_total=3,
            cantidad_disponible=3,
        )
        self.loan = Prestamo.objects.create(
            equipo=self.equipment,
            solicitante=self.student,
            fecha=timezone.localdate() + timedelta(days=1),
            horario="09:00 - 11:00",
            proyecto="Electrónica",
            motivo="Uso del equipo para práctica de señales y medición.",
            cantidad=2,
        )

    def test_approving_loan_updates_available_inventory(self):
        self.client.force_authenticate(self.tecnico)

        response = self.client.patch(
            f"/api/prestamos/{self.loan.id}/estado/",
            {"estado": "Aprobado"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.loan.refresh_from_db()
        self.equipment.refresh_from_db()
        self.assertEqual(self.loan.estado, "Aprobado")
        self.assertEqual(self.equipment.cantidad_disponible, 1)
        self.assertEqual(self.equipment.estado, "En Préstamo")

# Create your tests here.
