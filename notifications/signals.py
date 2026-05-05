from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='gigs.GigApplication')
def on_application_saved(sender, instance, **kwargs):
    from .service import notify_application_accepted, notify_application_declined

    if instance.status == 'accepted':
        notify_application_accepted(instance)
    elif instance.status == 'declined':
        notify_application_declined(instance)
