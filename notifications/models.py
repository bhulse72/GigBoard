from django.db import models
from django.conf import settings


class Notification(models.Model):
    VERIFY_GIG = 'verify_gig'
    LEAVE_REVIEW = 'leave_review'
    GIG_INVITE = 'gig_invite'
    TYPE_CHOICES = [
        (VERIFY_GIG, 'Verify Gig Completion'),
        (LEAVE_REVIEW, 'Leave a Review'),
        (GIG_INVITE, 'Gig Invitation'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_application = models.ForeignKey(
        'gigs.GigApplication',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    related_listing = models.ForeignKey(
        'gigs.GigListing',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='invite_notifications',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('recipient', 'notification_type', 'related_application')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient} — {self.notification_type}"
