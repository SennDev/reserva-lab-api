from rest_framework import status
from rest_framework.test import APITestCase

from apps.equipment.models import Equipo
from apps.labs.models import Laboratorio
from apps.users.models import User


class EquipmentApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email="admin@reservalab.local",
            password="Admin1234",
            first_name="Admin",
            last_name="User",
            matricula="EMP000001",
            carrera_departamento="Administración",
            tipo_usuario="personal",
            rol="admin",
        )
        self.lab = Laboratorio.objects.create(
            nombre="Laboratorio de Pruebas",
            edificio="CCO9",
            tipo="Cómputo",
            capacidad=20,
            estado="Disponible",
            equipamiento=["PCs", "Proyector"],
        )
        self.equipment = Equipo.objects.create(
            nombre="Equipo de Medición Pro",
            numero_serie="SN-TEST-1001",
            laboratorio=self.lab,
            ubicacion=self.lab.nombre,
            estado="Disponible",
            cantidad_total=5,
            cantidad_disponible=5,
        )

    def test_delete_soft_deletes_equipment(self):
        self.client.force_authenticate(self.admin)

        response = self.client.delete(f"/api/equipos/{self.equipment.id}/")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.equipment.refresh_from_db()
        self.assertEqual(self.equipment.estado, "Baja")
        self.assertEqual(self.equipment.cantidad_disponible, 0)

# Create your tests here.
