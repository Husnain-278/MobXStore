from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .email_service import notify_order_status_change
from .models import Order


@receiver(pre_save, sender=Order)
def capture_previous_status(sender, instance, **kwargs):
    """Stash the order's status before it is overwritten by the save.

    Uses an instance-private attribute because post_save no longer has
    access to the pre-save database value. Note: queryset .update() calls
    bypass signals entirely and are therefore not handled here.
    """
    instance._previous_status = None
    if instance.pk:
        instance._previous_status = (
            sender.objects.filter(pk=instance.pk)
            .values_list("status", flat=True)
            .first()
        )


@receiver(post_save, sender=Order)
def send_status_update_email(sender, instance, created, **kwargs):
    """Email the customer whenever an existing order changes status.

    Runs for every save path (admin panel, chat agent tool, services),
    which guarantees the notification regardless of where the change
    originated. New orders are skipped — the order confirmation email
    covers those.
    """
    if created:
        return

    previous_status = getattr(instance, "_previous_status", None)
    if previous_status:
        notify_order_status_change(instance, previous_status)