from django.urls import path
from . import views

app_name = 'gigs'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('create/', views.create_listing, name='create_listing'),
    path('mine/', views.my_listings, name='my_listings'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.calendar_events, name='calendar_events'),
    path('<int:pk>/close/', views.close_listing, name='close_listing'),
    path('<int:pk>/apply/', views.apply_to_gig, name='apply'),
    path('<int:pk>/applications/', views.listing_applications, name='listing_applications'),
    path('applications/<int:pk>/update/', views.update_application, name='update_application'),
    path('applications/<int:pk>/verify/', views.verify_gig_completion, name='verify_completion'),
    path('invite/<int:performer_id>/', views.invite_performer, name='invite_performer'),
    path('listings/<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('bookings/', views.my_bookings, name='my_bookings'),
]