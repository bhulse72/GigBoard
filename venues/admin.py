from django.contrib import admin
from .models import Venue, VenueManager

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'city', 'state', 'capacity')
    search_fields = ('name', 'city')

@admin.register(VenueManager)
class VenueManagerAdmin(admin.ModelAdmin):
    list_display = ('user', 'venue', 'assigned_at')