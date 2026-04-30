from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.equipment.models import Equipo
from apps.labs.models import Laboratorio
from apps.loans.models import Prestamo
from apps.reservations.models import Reserva
from apps.users.models import User


class Command(BaseCommand):
    help = "Carga usuarios, laboratorios, equipos, reservas y préstamos demo para ReservaLab."

    def handle(self, *args, **options):
        today = timezone.localdate()

        admin = self._upsert_user(
            email="admin@reservalab.local",
            password="Admin1234",
            first_name="Gerson",
            last_name="Contreras",
            matricula="EMP000001",
            carrera_departamento="Administración FCC",
            tipo_usuario="personal",
            rol="admin",
            is_superuser=True,
            is_staff=True,
        )
        tecnico = self._upsert_user(
            email="tecnico@reservalab.local",
            password="Tecnico1234",
            first_name="Dulce",
            last_name="Aranza",
            matricula="EMP000002",
            carrera_departamento="Soporte de Laboratorios",
            tipo_usuario="personal",
            rol="tecnico",
            is_staff=True,
        )
        estudiante = self._upsert_user(
            email="estudiante@reservalab.local",
            password="Estudiante1234",
            first_name="Pablo",
            last_name="Ibarra Valencia",
            matricula="202301234",
            carrera_departamento="Ciencias de la Computación",
            tipo_usuario="estudiante",
            rol="estudiante",
        )

        labs = {
            "LAB-CCO1": Laboratorio.objects.update_or_create(
                pk="LAB-CCO1",
                defaults={
                    "nombre": "Laboratorio de Computación Avanzada",
                    "edificio": "Edificio CCO1",
                    "tipo": "Cómputo",
                    "capacidad": 35,
                    "estado": "Disponible",
                    "equipamiento": ["Workstations", "Proyector Interactivo", "Pizarrón Inteligente"],
                },
            )[0],
            "LAB-CCO2": Laboratorio.objects.update_or_create(
                pk="LAB-CCO2",
                defaults={
                    "nombre": "Laboratorio de Redes y Seguridad",
                    "edificio": "Edificio CCO2",
                    "tipo": "Redes",
                    "capacidad": 25,
                    "estado": "En Mantenimiento",
                    "equipamiento": ["Routers Cisco", "Switches", "Racks de Servidores"],
                },
            )[0],
            "LAB-FIS1": Laboratorio.objects.update_or_create(
                pk="LAB-FIS1",
                defaults={
                    "nombre": "Laboratorio de Hardware y Robótica",
                    "edificio": "Edificio CCO3",
                    "tipo": "Robótica",
                    "capacidad": 20,
                    "estado": "Disponible",
                    "equipamiento": ["Osciloscopios", "Kits Arduino", "Impresoras 3D"],
                },
            )[0],
        }

        Equipo.objects.update_or_create(
            pk="EQ-001",
            defaults={
                "nombre": "Osciloscopio Digital Rigol",
                "numero_serie": "SN-RIG-8472",
                "laboratorio": labs["LAB-FIS1"],
                "ubicacion": labs["LAB-FIS1"].nombre,
                "estado": "Disponible",
                "cantidad_total": 3,
                "cantidad_disponible": 2,
            },
        )
        Equipo.objects.update_or_create(
            pk="EQ-002",
            defaults={
                "nombre": "Router Cisco 2901",
                "numero_serie": "SN-CIS-9921",
                "laboratorio": labs["LAB-CCO2"],
                "ubicacion": labs["LAB-CCO2"].nombre,
                "estado": "Mantenimiento",
                "cantidad_total": 4,
                "cantidad_disponible": 4,
            },
        )
        Equipo.objects.update_or_create(
            pk="EQ-003",
            defaults={
                "nombre": "Kit Arduino Mega 2560",
                "numero_serie": "SN-ARD-1104",
                "laboratorio": None,
                "ubicacion": "Almacén Central",
                "estado": "Disponible",
                "cantidad_total": 10,
                "cantidad_disponible": 10,
            },
        )

        Reserva.objects.update_or_create(
            pk="RES-001",
            defaults={
                "laboratorio": labs["LAB-CCO1"],
                "solicitante": estudiante,
                "fecha": today + timedelta(days=1),
                "horario": "13:00 - 15:00",
                "materia": "Desarrollo Web",
                "motivo": "Práctica de laboratorio para el proyecto final.",
                "estado": "Aprobada",
            },
        )
        Reserva.objects.update_or_create(
            pk="RES-002",
            defaults={
                "laboratorio": labs["LAB-FIS1"],
                "solicitante": estudiante,
                "fecha": today + timedelta(days=2),
                "horario": "15:00 - 17:00",
                "materia": "Arquitectura de Computadoras",
                "motivo": "Uso de equipo para práctica de medición y diagnóstico.",
                "estado": "Pendiente",
            },
        )

        equipo_demo = Equipo.objects.get(pk="EQ-001")
        Prestamo.objects.update_or_create(
            pk="PR-001",
            defaults={
                "equipo": equipo_demo,
                "solicitante": estudiante,
                "fecha": today + timedelta(days=1),
                "horario": "09:00 - 11:00",
                "proyecto": "Electrónica Digital",
                "motivo": "Uso del osciloscopio para captura y validación de señales.",
                "cantidad": 1,
                "estado": "Aprobado",
            },
        )

        self.stdout.write(self.style.SUCCESS("Datos demo cargados correctamente."))
        self.stdout.write("Credenciales demo:")
        self.stdout.write("  admin@reservalab.local / Admin1234")
        self.stdout.write("  tecnico@reservalab.local / Tecnico1234")
        self.stdout.write("  estudiante@reservalab.local / Estudiante1234")

    def _upsert_user(self, email, password, **defaults):
        user, _ = User.objects.update_or_create(email=email, defaults=defaults)
        user.set_password(password)
        user.save()
        return user
