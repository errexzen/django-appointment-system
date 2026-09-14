# API Guide

Base path: `/api/v1/`

## Auth
- `POST /api/register/`
- `POST /api/login/`
- `POST /api/token/refresh/`
- `POST /api/logout/`
- `POST /api/verify-email/`
- `POST /api/forgot-password/`
- `POST /api/reset-password/`

## Organization
- `GET/PATCH /api/organizations/current/`
- `GET /api/organizations/memberships/`
- `POST /api/organizations/invitations/`
- `POST /api/organizations/invitations/accept/`

## Services, Staff, Scheduling
- `/api/v1/services/`
- `/api/v1/service-categories/`
- `/api/v1/staff/`
- `/api/v1/availability/weekly/`
- `/api/v1/availability/exceptions/`
- `/api/v1/availability/time-off/`
- `/api/v1/availability/holidays/`
- `/api/v1/availability/slots/available-slots/`

## Bookings and customers
- `/api/v1/bookings/`
- `/api/v1/bookings/{id}/cancel/`
- `/api/v1/bookings/{id}/reschedule/`
- `/api/v1/bookings/{id}/update_status/`
- `/api/v1/customers/`
- `/api/v1/waitlist/`

## Documentation
- Schema: `/api/schema/`
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
