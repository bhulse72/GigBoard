"""
Central service for creating notifications.

All notification creation goes through this module — views and signal handlers
call these functions rather than touching the Notification model directly.
Adding a new notification type means adding a function here and wiring up
whatever triggers it (a view action or a signal).
"""

from .models import Notification


def notify_gig_invite(performer, listing):
    """Invite a performer to apply for an open gig listing. Returns False if already invited."""
    already_invited = Notification.objects.filter(
        recipient=performer,
        notification_type=Notification.GIG_INVITE,
        related_listing=listing,
    ).exists()
    if already_invited:
        return False
    Notification.objects.create(
        recipient=performer,
        notification_type=Notification.GIG_INVITE,
        related_listing=listing,
        message=(
            f'{listing.venue_name} has invited you to apply for "{listing.title}" '
            f'on {listing.event_date.strftime("%B %-d, %Y")}.'
        ),
    )
    return True


def notify_application_accepted(application):
    """Notify a performer that their gig application was accepted."""
    Notification.objects.get_or_create(
        recipient=application.performer,
        notification_type=Notification.APPLICATION_ACCEPTED,
        related_application=application,
        defaults={
            'message': (
                f'Your application for "{application.listing.title}" at '
                f'{application.listing.venue_name} has been accepted!'
            )
        },
    )


def notify_application_declined(application):
    """Notify a performer that their gig application was declined."""
    Notification.objects.get_or_create(
        recipient=application.performer,
        notification_type=Notification.APPLICATION_DECLINED,
        related_application=application,
        defaults={
            'message': (
                f'Your application for "{application.listing.title}" at '
                f'{application.listing.venue_name} was not accepted this time.'
            )
        },
    )


def notify_collab_request_received(collab_request):
    """Notify a performer that someone sent them a collaboration request."""
    sender_name = collab_request.sender.stage_name or collab_request.sender.username
    Notification.objects.get_or_create(
        recipient=collab_request.receiver,
        notification_type=Notification.COLLAB_REQUEST_RECEIVED,
        related_collab_request=collab_request,
        defaults={
            'message': f'{sender_name} sent you a collaboration request.',
        },
    )


def notify_collab_request_accepted(collab_request):
    """Notify a performer that their collaboration request was accepted."""
    receiver_name = collab_request.receiver.stage_name or collab_request.receiver.username
    Notification.objects.get_or_create(
        recipient=collab_request.sender,
        notification_type=Notification.COLLAB_REQUEST_ACCEPTED,
        related_collab_request=collab_request,
        defaults={
            'message': f'{receiver_name} accepted your collaboration request.',
        },
    )


def notify_collab_request_declined(collab_request):
    """Notify a performer that their collaboration request was declined."""
    receiver_name = collab_request.receiver.stage_name or collab_request.receiver.username
    Notification.objects.get_or_create(
        recipient=collab_request.sender,
        notification_type=Notification.COLLAB_REQUEST_DECLINED,
        related_collab_request=collab_request,
        defaults={
            'message': f'{receiver_name} declined your collaboration request.',
        },
    )


def _notify_verify_gig(recipient, app, message):
    Notification.objects.get_or_create(
        recipient=recipient,
        notification_type=Notification.VERIFY_GIG,
        related_application=app,
        defaults={'message': message},
    )


def _swap_to_leave_review(recipient, app, message):
    Notification.objects.filter(
        recipient=recipient,
        notification_type=Notification.VERIFY_GIG,
        related_application=app,
    ).delete()
    Notification.objects.get_or_create(
        recipient=recipient,
        notification_type=Notification.LEAVE_REVIEW,
        related_application=app,
        defaults={'message': message},
    )


def generate_gig_notifications(user):
    """
    Idempotently creates verify/review notifications for past gigs.
    Safe to call on every profile or inbox page load.
    """
    from django.utils import timezone
    from gigs.models import GigApplication
    from venues.models import Venue, VenueManager

    today = timezone.now().date()

    if user.is_performer():
        past_apps = GigApplication.objects.filter(
            performer=user,
            status='accepted',
            listing__event_date__lt=today,
        ).select_related('listing', 'listing__venue')

        for app in past_apps:
            if app.is_verified_complete:
                _swap_to_leave_review(
                    user, app,
                    f'Your gig "{app.listing.title}" at {app.listing.venue_name} '
                    f'is verified complete. Leave a review!',
                )
            elif not app.performer_verified_complete:
                _notify_verify_gig(
                    user, app,
                    f'Did your gig "{app.listing.title}" at '
                    f'{app.listing.venue_name} on {app.listing.event_date} '
                    f'take place? Please verify on your profile.',
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
                _swap_to_leave_review(
                    user, app,
                    f'Your gig "{app.listing.title}" with {performer_display} '
                    f'is verified complete. Leave a review!',
                )
            elif not app.venue_verified_complete:
                _notify_verify_gig(
                    user, app,
                    f'Did the gig "{app.listing.title}" with {performer_display} '
                    f'on {app.listing.event_date} take place? '
                    f'Please verify on your venue management page.',
                )
