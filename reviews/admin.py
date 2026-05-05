from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewer_role', 'reviewed_performer', 'reviewed_venue', 'rating', 'is_edited', 'created_at')
    list_filter = ('reviewer_role', 'is_edited')
    search_fields = ('reviewer__username', 'title')
