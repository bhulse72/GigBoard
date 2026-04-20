from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        VENUE_OWNER = 'venue_owner', 'Venue Owner'
        MANAGER = 'manager', 'Manager'
        PERFORMER = 'performer', 'Performer'
        FAN = 'fan', 'Fan'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        null=True,
        blank=True,
    )
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)

    stage_name = models.CharField(max_length=100, blank=True)
    music_style = models.CharField(max_length=100, blank=True)
    interests = models.CharField(max_length=255, blank=True)
    soundcloud_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    spotify_url = models.URLField(blank=True)

    def is_venue_owner(self):
        return self.role == self.Role.VENUE_OWNER

    def is_manager(self):
        return self.role == self.Role.MANAGER

    def is_performer(self):
        return self.role == self.Role.PERFORMER

    def is_fan(self):
        return self.role == self.Role.FAN

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'

