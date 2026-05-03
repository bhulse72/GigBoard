from django.urls import path
from . import views

app_name = 'fans'

urlpatterns = [
    path('performers/', views.performer_list, name='performer_list'),
    path('follow/<int:performer_id>/', views.follow_performer, name='follow_performer'),
    path('unfollow/<int:performer_id>/', views.unfollow_performer, name='unfollow_performer'),
    path('following/', views.my_following, name='my_following'),
    path('schedule/', views.followed_schedule, name='followed_schedule'),
]