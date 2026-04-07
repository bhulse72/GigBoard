from django.urls import path
from . import views

app_name = 'venues'

urlpatterns = [
    path('', views.venue_dashboard, name='dashboard'),
    path('create/', views.create_venue, name='create'),
    path('<int:pk>/select/', views.select_venue, name='select'),
    path('<int:pk>/manage/', views.manage_venue, name='manage'),
    path('<int:pk>/edit/', views.edit_venue, name='edit'),
]