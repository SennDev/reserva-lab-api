from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class AuthApiTests(APITestCase):
    def test_register_creates_student_user(self):
        payload = {
            "nombre": "Ana",
            "apellidos": "Martinez Lopez",
            "matricula": "202305678",
            "email": "ana@alumno.buap.mx",
            "carrera": "Ciencias de la Computación",
            "tipo_usuario": "estudiante",
            "password": "BuapStrong123",
            "confirm_password": "BuapStrong123",
        }

        response = self.client.post(reverse("auth-register"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["user"]["nombre_completo"], "Ana Martinez Lopez")
        self.assertEqual(response.data["user"]["rol"], "estudiante")
        self.assertTrue(User.objects.filter(email=payload["email"]).exists())

    def test_register_creates_admin_user(self):
        payload = {
            "nombre": "Gerson",
            "apellidos": "Contreras",
            "matricula": "EMP000099",
            "email": "admin.demo@reservalab.local",
            "carrera": "Administración FCC",
            "tipo_usuario": "admin",
            "password": "AdminStrong123",
            "confirm_password": "AdminStrong123",
        }

        response = self.client.post(reverse("auth-register"), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_user = User.objects.get(email=payload["email"])
        self.assertEqual(response.data["user"]["rol"], "admin")
        self.assertTrue(created_user.is_staff)
        self.assertTrue(created_user.is_superuser)

    def test_login_returns_tokens_and_user(self):
        user = User.objects.create_user(
            email="admin@reservalab.local",
            password="Admin1234",
            first_name="Gerson",
            last_name="Contreras",
            matricula="EMP000001",
            carrera_departamento="Administración FCC",
            tipo_usuario="personal",
            rol="admin",
        )

        response = self.client.post(
            reverse("auth-login"),
            {"email": user.email, "password": "Admin1234"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], user.email)

# Create your tests here.
