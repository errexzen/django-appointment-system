# Booking Engine

## Core principles
- Organization-scoped booking records.
- Transactional creation with row-level locking via `select_for_update`.
- Overlap conflict checks for active booking statuses.
- Immutable booking reference for external usage.

## Conflict prevention
- During creation, the service locks candidate rows and re-checks overlaps.
- Returns a clear validation error when slot was taken concurrently.

## Cancellation and rescheduling
- Cancellation writes status history and activity logs.
- Rescheduling creates a new booking and links `rescheduled_from`.
- Notification events are queued asynchronously.
