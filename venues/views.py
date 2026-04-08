from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Venue, VenueManager
from .forms import VenueForm
from gigs.models import GigListing


def can_manage_venue(user, venue):
    """Check if a user has management rights over a venue."""
    if user.is_venue_owner() and venue.owner == user:
        return True
    if user.is_manager() and VenueManager.objects.filter(user=user, venue=venue).exists():
        return True
    return False


@login_required
def venue_dashboard(request):
    """Shows all venues the logged in user can manage."""
    if request.user.is_venue_owner():
        venues = Venue.objects.filter(owner=request.user)
    elif request.user.is_manager():
        managed = VenueManager.objects.filter(user=request.user).select_related('venue')
        venues = [vm.venue for vm in managed]
    else:
        return redirect('core:home')
    return render(request, 'venues/dashboard.html', {'venues': venues})


@login_required
def select_venue(request, pk):
    """Sets the active venue in the session."""
    venue = get_object_or_404(Venue, pk=pk)
    if not can_manage_venue(request.user, venue):
        messages.error(request, 'You do not have access to that venue.')
        return redirect('venues:dashboard')
    request.session['active_venue_id'] = venue.pk
    request.session['active_venue_name'] = venue.name
    return redirect('venues:manage', pk=venue.pk)


@login_required
def manage_venue(request, pk):
    """Main management page for a specific venue."""
    venue = get_object_or_404(Venue, pk=pk)
    if not can_manage_venue(request.user, venue):
        messages.error(request, 'You do not have access to that venue.')
        return redirect('venues:dashboard')
    request.session['active_venue_id'] = venue.pk
    request.session['active_venue_name'] = venue.name
    return render(request, 'venues/manage.html', {'venue': venue})


@login_required
def create_venue(request):
    """Venue owners can create a new venue."""
    if not request.user.is_venue_owner():
        messages.error(request, 'Only venue owners can create venues.')
        return redirect('core:home')
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES)
        if form.is_valid():
            venue = form.save(commit=False)
            venue.owner = request.user
            venue.save()
            messages.success(request, f'{venue.name} has been created!')
            return redirect('venues:manage', pk=venue.pk)
    else:
        form = VenueForm()
    return render(request, 'venues/create.html', {'form': form})


@login_required
def edit_venue(request, pk):
    """Edit an existing venue's details."""
    venue = get_object_or_404(Venue, pk=pk)
    if not can_manage_venue(request.user, venue):
        messages.error(request, 'You do not have access to that venue.')
        return redirect('venues:dashboard')
    if request.method == 'POST':
        form = VenueForm(request.POST, request.FILES, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, 'Venue updated successfully.')
            return redirect('venues:manage', pk=venue.pk)
    else:
        form = VenueForm(instance=venue)
    return render(request, 'venues/edit.html', {'form': form, 'venue': venue})

@login_required
def manage_venue(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    if not can_manage_venue(request.user, venue):
        messages.error(request, 'You do not have access to that venue.')
        return redirect('venues:dashboard')
    request.session['active_venue_id'] = venue.pk
    request.session['active_venue_name'] = venue.name
    gig_listings = GigListing.objects.filter(venue=venue).order_by('-event_date')
    return render(request, 'venues/manage.html', {'venue': venue, 'gig_listings': gig_listings})