from django.contrib import admin
from .models import Notification, Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewer_role', 'reviewed_performer', 'reviewed_venue', 'rating', 'is_edited', 'created_at')
    list_filter = ('reviewer_role', 'is_edited')
    search_fields = ('reviewer__username', 'title')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__username', 'message')
