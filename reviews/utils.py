from django.utils import timezone


def generate_gig_notifications(user):
    """
    Idempotently creates in-app notifications for past gigs that need
    verification or a review. Safe to call on every profile page load.
    """
    from gigs.models import GigApplication
    from venues.models import Venue, VenueManager
    from notifications.models import Notification

    today = timezone.now().date()

    if user.is_performer():
        past_apps = GigApplication.objects.filter(
            performer=user,
            status='accepted',
            listing__event_date__lt=today,
        ).select_related('listing', 'listing__venue')

        for app in past_apps:
            if app.is_verified_complete:
                # Swap verify → leave_review
                Notification.objects.filter(
                    recipient=user,
                    notification_type=Notification.VERIFY_GIG,
                    related_application=app,
                ).delete()
                performer_name = app.listing.venue_name
                Notification.objects.get_or_create(
                    recipient=user,
                    notification_type=Notification.LEAVE_REVIEW,
                    related_application=app,
                    defaults={
                        'message': (
                            f'Your gig "{app.listing.title}" at {performer_name} '
                            f'is verified complete. Leave a review!'
                        )
                    },
                )
            elif not app.performer_verified_complete:
                Notification.objects.get_or_create(
                    recipient=user,
                    notification_type=Notification.VERIFY_GIG,
                    related_application=app,
                    defaults={
                        'message': (
                            f'Did your gig "{app.listing.title}" at '
                            f'{app.listing.venue_name} on {app.listing.event_date} '
                            f'take place? Please verify on your profile.'
                        )
                    },
                )

    if user.is_venue_owner() or user.is_manager():
        if user.is_venue_owner():
            venue_ids = list(Venue.objects.filter(owner=user).values_list('id', flat=True))
        else:
            venue_ids = list(
                VenueManager.objects.filter(user=user).values_list('venue_id', flat=True)
            )

        past_apps = GigApplication.objects.filter(
            listing__venue_id__in=venue_ids,
            status='accepted',
            listing__event_date__lt=today,
        ).select_related('listing', 'performer')

        for app in past_apps:
            performer_display = app.performer.stage_name or app.performer.username

            if app.is_verified_complete:
                Notification.objects.filter(
                    recipient=user,
                    notification_type=Notification.VERIFY_GIG,
                    related_application=app,
                ).delete()
                Notification.objects.get_or_create(
                    recipient=user,
                    notification_type=Notification.LEAVE_REVIEW,
                    related_application=app,
                    defaults={
                        'message': (
                            f'Your gig "{app.listing.title}" with {performer_display} '
                            f'is verified complete. Leave a review!'
                        )
                    },
                )
            elif not app.venue_verified_complete:
                Notification.objects.get_or_create(
                    recipient=user,
                    notification_type=Notification.VERIFY_GIG,
                    related_application=app,
                    defaults={
                        'message': (
                            f'Did the gig "{app.listing.title}" with {performer_display} '
                            f'on {app.listing.event_date} take place? '
                            f'Please verify on your venue management page.'
                        )
                    },
                )
