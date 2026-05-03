from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .models import PerformerFollow
from gigs.models import GigApplication

from datetime import date


@login_required
def performer_list(request):
    if not request.user.is_fan():
        messages.error(request, 'Only fans can access this page.')
        return redirect('accounts:profile')

    performers = User.objects.filter(role=User.Role.PERFORMER)

    followed_ids = PerformerFollow.objects.filter(
        fan=request.user
    ).values_list('performer_id', flat=True)

    return render(request, 'fans/performer_list.html', {
        'performers': performers,
        'followed_ids': followed_ids,
    })


@login_required
def follow_performer(request, performer_id):
    if not request.user.is_fan():
        messages.error(request, 'Only fans can follow performers.')
        return redirect('accounts:profile')

    performer = get_object_or_404(
        User,
        id=performer_id,
        role=User.Role.PERFORMER
    )

    if request.user == performer:
        messages.error(request, 'You cannot follow yourself.')
        return redirect('fans:performer_list')

    PerformerFollow.objects.get_or_create(
        fan=request.user,
        performer=performer
    )

    messages.success(request, 'Performer followed.')
    return redirect('fans:performer_list')


@login_required
def unfollow_performer(request, performer_id):
    if not request.user.is_fan():
        messages.error(request, 'Only fans can unfollow performers.')
        return redirect('accounts:profile')

    performer = get_object_or_404(
        User,
        id=performer_id,
        role=User.Role.PERFORMER
    )

    PerformerFollow.objects.filter(
        fan=request.user,
        performer=performer
    ).delete()

    messages.success(request, 'Performer unfollowed.')
    return redirect('fans:performer_list')


@login_required
def my_following(request):
    if not request.user.is_fan():
        messages.error(request, 'Only fans can access this page.')
        return redirect('accounts:profile')

    follows = PerformerFollow.objects.filter(
        fan=request.user
    ).select_related('performer')

    return render(request, 'fans/my_following.html', {
        'follows': follows,
    })

@login_required
def followed_schedule(request):
    if not request.user.is_fan():
        messages.error(request, 'Only fans can access this page.')
        return redirect('accounts:profile')
    
    followed_ids = PerformerFollow.objects.filter(
        fan=request.user
    ).values_list('performer_id', flat=True)

    upcoming_gigs = GigApplication.objects.filter(
        performer_id__in=followed_ids,
        status='accepted',
        listing__event_date__gte=date.today(),
    ).select_related(
        'performer',
        'listing',
        'listing__venue',
    ).order_by('listing__event_date', 'listing__start_time')

    return render(request, 'fans/followed_schedule.html', {
        'upcoming_gigs': upcoming_gigs,
    })