from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('venues/', include('venues.urls', namespace='venues')),
    path('gigs/', include('gigs.urls')),
    path('', include('core.urls')),
]