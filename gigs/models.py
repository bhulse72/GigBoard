from django.db import models
from django.conf import settings
from venues.models import Venue


class GigListing(models.Model):
    STYLE_CHOICES = [
        ('open_format', 'Open Format'),
        ('house', 'House'),
        ('hip_hop', 'Hip Hop'),
        ('edm', 'EDM'),
        ('acoustic', 'Acoustic'),
        ('band', 'Live Band'),
        ('other', 'Other'),
    ]

    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE,
        related_name='gig_listings',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200)
    venue_name = models.CharField(max_length=200)
    location = models.CharField(max_length=255, blank=True)
    event_date = models.DateField()
    start_time = models.TimeField()
    pay = models.DecimalField(max_digits=8, decimal_places=2)
    preferred_style = models.CharField(max_length=30, choices=STYLE_CHOICES)
    description = models.TextField(blank=True)
    is_open = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gig_listings'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.venue_name}"