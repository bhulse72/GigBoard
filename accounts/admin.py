from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('GigBoard', {'fields': ('role', 'bio', 'location', 'stage_name', 'music_style', 'interests')}),
    )
    list_display = ('username', 'email', 'role', 'is_staff')
