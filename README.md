# ReservaLab API

Backend inicial para `reserva-lab-webapp`, construido con Django, Django REST Framework y JWT.

## Alcance actual

- Autenticación JWT con login, registro, refresh, logout y `me`
- Usuarios con roles `admin`, `tecnico` y `estudiante`
- CRUD de laboratorios
- CRUD de equipos con cantidades y baja lógica
- Reservas con validación de choques de horario
- Préstamos con control básico de inventario
- Dashboard summary para el frontend Angular
- Seed de datos demo para pruebas locales

## Stack

- Django 6.0.4
- Django REST Framework
- SimpleJWT
- PyMySQL
- django-cors-headers
- django-filter

## Configuración

1. Instala dependencias:

```powershell
pip install -r requirements.txt
```

2. Crea tu archivo `.env` a partir de `.env.example`.

3. Para XAMPP + phpMyAdmin, usa estos valores base:

```env
DB_ENGINE=mysql
DB_NAME=reserva_lab_db
DB_USER=root
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3307
```

Si todavía no tienes credenciales definitivas, puedes cambiar temporalmente `DB_ENGINE=sqlite` para desarrollo local.

## Comandos principales

```powershell
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

## Usuarios demo

- `admin@reservalab.local` / `Admin1234`
- `tecnico@reservalab.local` / `Tecnico1234`
- `estudiante@reservalab.local` / `Estudiante1234`

## Endpoints principales

- `POST /api/auth/login/`
- `POST /api/auth/registro/`
- `POST /api/auth/token/refresh/`
- `POST /api/auth/logout/`
- `GET|PATCH /api/auth/me/`
- `GET|POST /api/laboratorios/`
- `GET /api/laboratorios/disponibles/`
- `GET|POST /api/equipos/`
- `GET|POST /api/reservas/`
- `PATCH /api/reservas/{id}/estado/`
- `GET|POST /api/prestamos/`
- `PATCH /api/prestamos/{id}/estado/`
- `GET /api/dashboard/summary/`

## Notas de integración con el frontend

- Los listados devuelven arreglos planos, no paginación DRF, para acoplarse mejor al frontend Angular actual.
- El serializer de usuario responde con `nombre`, `apellidos`, `nombre_completo`, `carrera` y `carrera_departamento` para cubrir el estado actual de la UI.
- Equipos acepta ubicación libre para soportar opciones como `Almacén Central`, además de laboratorio relacionado.
- Reservas y préstamos aceptan `laboratorioId` y `equipoId`, igual que los formularios del frontend.
