from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import EditProfileForm, RegisterForm
from reviews.utils import generate_gig_notifications

@login_required
def profile(request):
    generate_gig_notifications(request.user)
    context = {}
    today = timezone.now().date()

    if request.user.is_performer():
        from gigs.models import GigApplication
        accepted = GigApplication.objects.filter(
            performer=request.user, status='accepted'
        ).select_related('listing', 'listing__venue').order_by('listing__event_date')
        context['upcoming_gigs'] = [a for a in accepted if a.listing.event_date >= today]
        context['past_gigs'] = [a for a in accepted if a.listing.event_date < today]

    elif request.user.is_venue_owner() or request.user.is_manager():
        from gigs.models import GigApplication
        from venues.models import Venue, VenueManager
        if request.user.is_venue_owner():
            venue_ids = list(Venue.objects.filter(owner=request.user).values_list('id', flat=True))
        else:
            venue_ids = list(VenueManager.objects.filter(user=request.user).values_list('venue_id', flat=True))
        context['past_venue_gigs'] = GigApplication.objects.filter(
            listing__venue_id__in=venue_ids,
            status='accepted',
            listing__event_date__lt=today,
        ).select_related('listing', 'listing__venue', 'performer').order_by('-listing__event_date')

    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = EditProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('accounts:profile')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})