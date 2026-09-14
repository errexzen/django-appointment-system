# Schedula Implementation Plan

Date: 2026-07-19
Execution mode: Incremental, migration-safe, production-oriented.

## Phase 1: Foundation and Settings
- Add `core` app for shared models, utilities, audit, health endpoints.
- Upgrade settings to environment-driven config with `django-environ`.
- Add PostgreSQL primary config and sqlite fallback.
- Add Redis/Celery config, secure cookie and deployment settings.
- Add static/media handling with WhiteNoise.
- Keep existing APIs temporarily while introducing `/api/v1/`.

## Phase 2: Accounts, Organizations, Roles, Invitations
- Refactor `accounts.User` to email-first login with role metadata and profile fields.
- Add email verification token and password reset flows.
- Add organization model, membership model, invitation model.
- Implement tenant-scoped permission helpers and queryset scoping.
- Add invitation acceptance flow (new and existing user).

## Phase 3: Services, Staff, Scheduling
- Add service category/service models under tenant scope.
- Add staff profile model linked to user + organization.
- Add weekly availability, exceptions, time off, holidays.
- Add slot generation service that respects timezone, rules, bookings, and blocks.

## Phase 4: Booking Engine
- Replace simplistic `Appointment` with robust `Booking` domain model.
- Add booking reference format `SCH-YYYY-XXXXXX`.
- Enforce transactional creation and conflict checks using `select_for_update`.
- Add cancellation/reschedule policies and booking activity log.
- Add waitlist model and workflow.

## Phase 5: Notifications
- Add notification log model and email templates.
- Integrate Celery worker + beat for async sends and reminders.
- Add duplicate reminder protection and retry metadata.

## Phase 6: Dashboard and Analytics
- Add tenant dashboard selectors for KPIs and chart datasets.
- Add platform dashboard for superusers.
- Add efficient annotated querysets and avoid N+1.

## Phase 7: Subscriptions
- Add plan and subscription models.
- Add usage accounting and plan limit checks for staff/services/bookings.
- Add payment provider abstraction with mock provider and optional Stripe hooks.

## Phase 8: API v1
- Implement versioned DRF endpoints for auth/org/services/staff/availability/bookings/customers/dashboard.
- JWT with rotation and blacklist.
- Pagination/filter/search/ordering.
- OpenAPI schema + Swagger + ReDoc.

## Phase 9: Web UX
- Add Django templates with HTMX, Alpine.js, Tailwind, Chart.js.
- Add public booking flow by organization slug `/book/{slug}/`.
- Add dashboard pages and responsive accessible components.

## Phase 10: Quality, Ops, Docs
- Add pytest, factories, coverage and high-value tests (tenant isolation + concurrency).
- Add Ruff, Black, pre-commit, Makefile.
- Add Dockerfile + compose (web/db/redis/celery/celery-beat).
- Add GitHub Actions CI pipeline.
- Produce complete docs set and deployment readiness.

## Migration Strategy
- Use additive migrations.
- Preserve existing tables; add new models and bridge adapters.
- Backward compatible API aliases where feasible.
- Avoid destructive migration unless explicitly needed.

## Completion Gates Per Phase
- `python manage.py makemigrations --check`
- `python manage.py migrate`
- `python manage.py check`
- Phase-specific tests
- Resolve all introduced failures before next phase
