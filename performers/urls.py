from django.urls import path
from . import views

app_name = 'performers'

urlpatterns = [
    path('', views.performer_directory, name='directory'),
    path('requests/', views.my_requests, name='requests'),
    path('request/<int:user_id>/', views.send_collab_request, name='send_request'),
    path('requests/<int:request_id>/accept/', views.accept_collab_request, name='accept_request'),
    path('requests/<int:request_id>/decline/', views.decline_collab_request, name='decline_request'),
]