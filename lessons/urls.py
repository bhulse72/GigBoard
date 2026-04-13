from django.urls import path
from . import views

app_name = 'lessons'

urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('create/', views.create_listing, name='create_listing'),
    path('mine/', views.my_listings, name='my_listings'),
    path('bookings/', views.my_bookings, name='my_bookings'),
    path('<int:pk>/', views.listing_detail, name='listing_detail'),
    path('<int:pk>/slot/add/', views.add_slot, name='add_slot'),
    path('<int:pk>/book/<int:slot_pk>/', views.book_slot, name='book_slot'),
    path('students/', views.my_students, name='my_students'),
]