from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from reviews.utils import generate_gig_notifications
from .models import Notification


@login_required
def notifications_inbox(request):
    generate_gig_notifications(request.user)
    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        'related_application',
        'related_application__listing',
        'related_application__listing__venue',
        'related_application__performer',
        'related_listing',
    )
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications/notifications.html', {'notifications': notifications})


@login_required
def dismiss_notification(request, notification_id):
    if request.method == 'POST':
        notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
        notif.delete()
    return redirect('notifications:inbox')
