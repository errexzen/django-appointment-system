import logging

from django.conf import settings

from notifications.models import NotificationLog
from notifications.tasks import send_templated_email


logger = logging.getLogger(__name__)


def queue_booking_notification(*, booking, notification_type: str, subject: str, template_base: str, recipient_email: str, recipient_user=None):
    log = NotificationLog.objects.create(
        organization=booking.organization,
        recipient=recipient_user,
        recipient_email=recipient_email,
        notification_type=notification_type,
        related_booking=booking,
        status=NotificationLog.Status.PENDING,
    )
    payload = {
        "notification_log_id": str(log.id),
        "subject": subject,
        "template_base": template_base,
        "context": {"booking": booking},
    }
    try:
        if settings.DEBUG:
            send_templated_email.apply(kwargs=payload)
        else:
            send_templated_email.delay(**payload)
    except Exception:  # pragma: no cover
        logger.warning("Falling back to sync email task execution", exc_info=True)
        send_templated_email.apply(kwargs=payload)
    return log
