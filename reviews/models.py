from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from venues.models import Venue


class Review(models.Model):
    ROLE_FAN = 'fan'
    ROLE_PERFORMER = 'performer'
    ROLE_VENUE = 'venue'
    REVIEWER_ROLE_CHOICES = [
        (ROLE_FAN, 'Fan'),
        (ROLE_PERFORMER, 'Performer'),
        (ROLE_VENUE, 'Venue'),
    ]

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
    )
    reviewer_role = models.CharField(max_length=20, choices=REVIEWER_ROLE_CHOICES)

    # Set when the reviewer is acting on behalf of a venue (owner or manager).
    # This is the authoritative identity for venue-authored reviews so that
    # the uniqueness constraint is per-venue, not per-user.
    reviewing_venue = models.ForeignKey(
        Venue,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='reviews_given',
    )

    # Exactly one of these will be set per review
    reviewed_performer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='reviews_received',
    )
    reviewed_venue = models.ForeignKey(
        Venue,
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='reviews_received',
    )

    # Links the review to the qualifying gig (null for fans)
    related_application = models.ForeignKey(
        'gigs.GigApplication',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='reviews',
    )

    title = models.CharField(max_length=150)
    rating = models.DecimalField(
        max_digits=3, decimal_places=1,
        validators=[MinValueValidator(0.0), MaxValueValidator(5.0)],
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)

    class Meta:
        constraints = [
            # One review per individual user per performer (fans and performers)
            models.UniqueConstraint(
                fields=['reviewer', 'reviewed_performer'],
                condition=models.Q(
                    reviewed_performer__isnull=False,
                    reviewing_venue__isnull=True,
                ),
                name='unique_user_performer_review',
            ),
            # One review per individual user per venue (fans and performers)
            models.UniqueConstraint(
                fields=['reviewer', 'reviewed_venue'],
                condition=models.Q(reviewed_venue__isnull=False),
                name='unique_user_venue_review',
            ),
            # One review per venue per performer
            models.UniqueConstraint(
                fields=['reviewing_venue', 'reviewed_performer'],
                condition=models.Q(
                    reviewing_venue__isnull=False,
                    reviewed_performer__isnull=False,
                ),
                name='unique_venue_performer_review',
            ),
        ]

    def __str__(self):
        target = self.reviewed_performer or self.reviewed_venue
        return f"{self.reviewer} → {target} ({self.rating}★)"


