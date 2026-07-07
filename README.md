# appointment_system

Professional appointment booking backend built with Django and Django REST Framework.

## Project Description

`appointment_system` is an API-first appointment reservation platform where users can register, authenticate with JWT, browse specialists, view specialist working hours, and book/cancel appointments.

The project follows clean architecture principles with separated apps:

- `accounts`
- `specialists`
- `appointments`
- `config` (project core)

## Features

- Custom user model with phone number field
- Registration, login, logout, profile endpoints
- JWT authentication via Simple JWT
- Specialist CRUD (admin write, public read)
- Specialist profession search
- Working hour management for specialists
- Appointment booking workflow with statuses (`pending`, `confirmed`, `cancelled`)
- Duplicate slot prevention for active appointments
- Working-hours validation for booking
- Django admin customization (filters/search)
- OpenAPI/Swagger docs using drf-spectacular
- Automated tests for core use cases

## Tech Stack

- Python
- Django
- Django REST Framework
- Simple JWT
- drf-spectacular
- SQLite (development)
- PostgreSQL-ready configuration via environment variables

## Installation Steps

1. Clone repository:

```bash
git clone <your-repo-url>
cd django-appointment-system
```

2. Create virtual environment and activate:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create env file:

```bash
copy .env.example .env
```

5. Run migrations:

```bash
python manage.py migrate
```

6. Create superuser:

```bash
python manage.py createsuperuser
```

7. Start development server:

```bash
python manage.py runserver
```

## Environment Setup

Main environment variables:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `TIME_ZONE`
- `DB_ENGINE` (`sqlite` or `postgres`)
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `JWT_ACCESS_MINUTES`
- `JWT_REFRESH_DAYS`

## API Documentation

- Swagger UI: `/api/docs/`
- OpenAPI schema: `/api/schema/`

## Main API Endpoints

Authentication:

- `POST /api/register/`
- `POST /api/login/`
- `POST /api/logout/`
- `GET /api/profile/`

Specialists:

- `GET /api/specialists/`
- `GET /api/specialists/<id>/`
- `GET /api/specialists/<id>/working-hours/`

Appointments:

- `POST /api/appointments/`
- `GET /api/my-appointments/`
- `PATCH /api/appointments/<id>/cancel/`
- `PATCH /api/appointments/<id>/confirm/` (admin only)

## Running Tests

```bash
python manage.py test
```

## Screenshots

Add screenshots in this section when UI clients or admin customizations are showcased:

- Admin specialist management page
- Swagger docs page
- Example appointment flow response screenshots

## Future Improvements

- Add time-slot generation endpoint for each specialist/day
- Add email/SMS notification service for appointment status updates
- Add rate limiting and audit logging
- Add Docker and CI/CD pipelines
- Add role-based permissions with `doctor`, `patient`, `staff` roles
