from django.db import models
from django.conf import settings

# Create your models here.

class PerformerFollow(models.Model):
    fan = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following_relationships'
    )
    performer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='follower_relationships'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('fan', 'performer')

    def __str__(self):
        return f"{self.fan.username} follows {self.performer.username}"
