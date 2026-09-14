# Existing Project Audit

Date: 2026-07-19
Project: Schedula (refactor target: django-appointment-system)

## 1. Repository State
- Active git root is repository top-level.
- There is an untracked nested duplicate folder `django-appointment-system/` inside the repo that mirrors the project. It is not part of tracked code and should not be used as the application root.
- Main tracked apps: `accounts`, `specialists`, `appointments`, `config`.

## 2. Existing Apps and Functionality

### accounts
- Custom user model extends `AbstractUser` with `phone_number` only.
- Auth API:
  - Register
  - Login (JWT pair)
  - Logout (refresh blacklist)
  - Profile (read current user)
- Gaps:
  - Username-based login, not email-first.
  - No role system.
  - No email verification.
  - No password reset flow.
  - No login history/audit.

### specialists
- Models:
  - `Specialist` (name, profession, description, image, created_at)
  - `WorkingHour` (weekday, time range, specialist)
- API:
  - CRUD for specialist (writes admin-only)
  - Specialist working-hours listing
- Gaps:
  - Not tenant-aware.
  - No service catalog.
  - No staff profile model tied to user/org.

### appointments
- Model:
  - `Appointment` (user, specialist, date, time, status)
  - Conditional unique constraint prevents active double booking for same specialist/date/time.
- API:
  - Create appointment
  - List own appointments
  - Cancel (owner/admin)
  - Confirm (admin)
- Gaps:
  - Not tenant-aware.
  - No timezone-safe datetime model.
  - No cancellation/reschedule policies.
  - No booking reference/public UUID.
  - No booking history/activity log.
  - No waitlist.

### config
- DRF + JWT + drf-spectacular enabled.
- PostgreSQL toggle via `DB_ENGINE`, otherwise sqlite.
- Security baseline exists but production hardening is incomplete.

## 3. Existing URLs
- Root redirects to Swagger.
- APIs mounted at `/api/` with flat endpoints.
- OpenAPI currently at `/api/schema/`, Swagger `/api/docs/`.

## 4. Existing Tests
- Basic API tests exist for accounts/specialists/appointments.
- No pytest stack.
- No tenant isolation tests.
- No concurrency tests.
- No coverage tooling.

## 5. Existing Dependencies
- Django 6.0.7, DRF, simplejwt, drf-spectacular, django-filter, pillow, psycopg.
- Missing: celery, redis client, django-environ, whitenoise, gunicorn, pytest stack, quality tooling.

## 6. What Should Be Preserved
- Existing custom user base and authentication concept.
- DRF and drf-spectacular foundation.
- Appointment anti-duplicate concept (to be upgraded to robust transactional slot protection).
- Existing app names can be bridged for backward compatibility where practical.

## 7. What Needs Refactoring
- Move to robust multi-tenant architecture with organization-scoped data.
- Replace date+time appointments with timezone-safe datetime intervals.
- Implement service layer and selector patterns for booking logic.
- Introduce role-based access and invitations.
- Harden settings for production and environment-based config.

## 8. What Needs to Be Added
- Organization/membership/role system.
- Services, categories, staff profiles, scheduling engine, exceptions, holidays, time off.
- Booking engine with transactional conflict safety, history, waitlist.
- Notifications (email + celery + reminder scheduling + logs).
- Dashboard analytics and platform admin metrics.
- Subscription plans and limit enforcement.
- Versioned API (`/api/v1/`) and JWT email-based auth flows.
- Template-based web UI (HTMX + Alpine.js + Tailwind + Chart.js).
- Docker, compose stack, CI, security docs, deployment docs.

## 9. Risk Notes
- Existing migration history is minimal and can be expanded safely via additive migrations.
- Duplicate untracked nested folder can cause confusion during local runs; commands should target repository root.
- Existing SQLite file is present; project must shift to PostgreSQL-first while keeping sqlite fallback for lightweight test/local usage.
