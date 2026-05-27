from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.labs.models import Laboratorio
from apps.reservations.models import Reserva
from apps.users.models import User


class ReservationApiTests(APITestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            email="student1@alumno.buap.mx",
            password="Student123",
            first_name="Ana",
            last_name="Martinez",
            matricula="202300001",
            carrera_departamento="Ciencias de la Computación",
            tipo_usuario="estudiante",
            rol="estudiante",
        )
        self.student_two = User.objects.create_user(
            email="student2@alumno.buap.mx",
            password="Student123",
            first_name="Luis",
            last_name="Gomez",
            matricula="202300002",
            carrera_departamento="Ciencias de la Computación",
            tipo_usuario="estudiante",
            rol="estudiante",
        )
        self.tecnico = User.objects.create_user(
            email="tecnico@reservalab.local",
            password="Tecnico1234",
            first_name="Dulce",
            last_name="Aranza",
            matricula="EMP000002",
            carrera_departamento="Laboratorios",
            tipo_usuario="personal",
            rol="tecnico",
        )
        self.lab = Laboratorio.objects.create(
            nombre="Laboratorio de Redes Seguras",
            edificio="CCO2",
            tipo="Redes",
            capacidad=25,
            estado="Disponible",
            equipamiento=["Switches", "Routers"],
        )
        self.future_date = timezone.localdate() + timedelta(days=2)

    def test_student_only_sees_own_reservations(self):
        Reserva.objects.create(
            laboratorio=self.lab,
            solicitante=self.student,
            fecha=self.future_date,
            horario="09:00 - 11:00",
            materia="Redes",
            motivo="Práctica de configuración segura en laboratorio.",
        )
        Reserva.objects.create(
            laboratorio=self.lab,
            solicitante=self.student_two,
            fecha=self.future_date + timedelta(days=1),
            horario="11:00 - 13:00",
            materia="Seguridad",
            motivo="Simulación de laboratorio con otro estudiante.",
        )

        self.client.force_authenticate(self.student)
        response = self.client.get("/api/reservas/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["solicitante"], self.student.nombre_completo)

    def test_pending_reservations_can_overlap_before_approval(self):
        Reserva.objects.create(
            laboratorio=self.lab,
            solicitante=self.student,
            fecha=self.future_date,
            horario="13:00 - 15:00",
            materia="Desarrollo Web",
            motivo="Uso del laboratorio para práctica integradora.",
            estado="Pendiente",
        )

        self.client.force_authenticate(self.student_two)
        response = self.client.post(
            "/api/reservas/",
            {
                "laboratorioId": self.lab.id,
                "fecha": self.future_date.isoformat(),
                "horario": "13:00 - 15:00",
                "materia": "Arquitectura",
                "motivo": "Nueva solicitud que choca con una reserva existente.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["estado"], "Pendiente")

    def test_approved_reservation_overlap_is_rejected(self):
        Reserva.objects.create(
            laboratorio=self.lab,
            solicitante=self.student,
            fecha=self.future_date,
            horario="13:00 - 15:00",
            materia="Desarrollo Web",
            motivo="Uso del laboratorio para práctica integradora.",
            estado="Aprobada",
        )

        self.client.force_authenticate(self.student_two)
        response = self.client.post(
            "/api/reservas/",
            {
                "laboratorioId": self.lab.id,
                "fecha": self.future_date.isoformat(),
                "horario": "13:00 - 15:00",
                "materia": "Arquitectura",
                "motivo": "Nueva solicitud que choca con una reserva aprobada.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("horario", response.data)

    def test_approving_overlapping_reservation_is_rejected(self):
        pending_reservation = Reserva.objects.create(
            laboratorio=self.lab,
            solicitante=self.student_two,
            fecha=self.future_date,
            horario="09:00 - 11:00",
            materia="Arquitectura",
            motivo="Solicitud pendiente con horario empalmado.",
        )
        Reserva.objects.create(
            laboratorio=self.lab,
            solicitante=self.student,
            fecha=self.future_date,
            horario="09:00 - 11:00",
            materia="Redes",
            motivo="Reserva aprobada previamente para validar empalmes.",
            estado="Aprobada",
        )

        self.client.force_authenticate(self.tecnico)
        response = self.client.patch(
            f"/api/reservas/{pending_reservation.id}/estado/",
            {"estado": "Aprobada"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("horario", response.data)

    def test_staff_can_update_status(self):
        reserva = Reserva.objects.create(
            laboratorio=self.lab,
            solicitante=self.student,
            fecha=self.future_date,
            horario="15:00 - 17:00",
            materia="Ciberseguridad",
            motivo="Reserva inicial pendiente de aprobación técnica.",
        )

        self.client.force_authenticate(self.tecnico)
        response = self.client.patch(
            f"/api/reservas/{reserva.id}/estado/",
            {"estado": "Aprobada"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.estado, "Aprobada")

# Create your tests here.
