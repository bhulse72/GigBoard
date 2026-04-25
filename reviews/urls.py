from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('performer/<int:user_id>/', views.submit_performer_review, name='review_performer'),
    path('venue/<int:venue_id>/', views.submit_venue_review, name='review_venue'),
    path('<int:review_id>/delete/', views.delete_review, name='delete_review'),
    path('notifications/', views.notifications_inbox, name='notifications'),
    path('notifications/<int:notification_id>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
]
