from django.urls import path 
from . import views

app_name = 'gigs'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('create/', views.create_listing, name='create_listing'),
    path('mine/', views.my_listings, name='my_listings'),
]