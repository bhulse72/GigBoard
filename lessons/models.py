from django.db import models
from django.conf import settings


class LessonListing(models.Model):
    STYLE_CHOICES = [
        ('guitar', 'Guitar'),
        ('piano', 'Piano'),
        ('vocals', 'Vocals'),
        ('drums', 'Drums'),
        ('bass', 'Bass'),
        ('dj', 'DJ / Production'),
        ('songwriting', 'Songwriting'),
        ('other', 'Other'),
    ]

    FORMAT_CHOICES = [
        ('in_person', 'In Person'),
        ('online', 'Online'),
        ('both', 'Both'),
    ]

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_listings',
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    style = models.CharField(max_length=50, choices=STYLE_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='both')
    location = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} by {self.instructor.username}'


class TimeSlot(models.Model):
    listing = models.ForeignKey(
        LessonListing,
        on_delete=models.CASCADE,
        related_name='time_slots',
    )
    date = models.DateField()
    start_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.listing.title} — {self.date} at {self.start_time}'

    class Meta:
        ordering = ['date', 'start_time']


class Booking(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
    )
    slot = models.OneToOneField(
        TimeSlot,
        on_delete=models.CASCADE,
        related_name='booking',
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.username} booked {self.slot}'
