from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notifications_inbox, name='inbox'),
    path('<int:notification_id>/dismiss/', views.dismiss_notification, name='dismiss'),
]
