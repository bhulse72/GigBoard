from django.urls import path
from . import views

app_name = 'performers'

urlpatterns = [
    path('', views.performer_directory, name='directory'),
    path('requests/', views.my_requests, name='requests'),
    path('request/<int:user_id>/', views.send_collab_request, name='send_request'),
    path('<int:user_id>/', views.performer_profile, name='profile'),
]