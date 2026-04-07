from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import GigListing
from .forms import GigListingForm
from venues.models import Venue


@login_required
def listing_list(request):
    listings = GigListing.objects.filter(is_open=True).order_by('event_date', 'start_time')
    
    # filtering
    style = request.GET.get('style')
    if style:
        listings = listings.filter(preferred_style=style)

    return render(request, 'gigs/listing_list.html', {
        'listings': listings,
        'style_choices': GigListing.STYLE_CHOICES,
        'selected_style': style,
    })


@login_required
def create_listing(request):
    if not (request.user.is_venue_owner() or request.user.is_manager()):
        messages.error(request, 'Only venue owners and managers can create listings.')
        return redirect('gigs:listing_list')

    # get active venue from session
    active_venue_id = request.session.get('active_venue_id')
    if not active_venue_id:
        messages.error(request, 'Please select a venue first.')
        return redirect('venues:dashboard')

    venue = get_object_or_404(Venue, pk=active_venue_id)

    if request.method == 'POST':
        form = GigListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.venue = venue
            listing.venue_name = venue.name
            listing.save()
            messages.success(request, 'Gig listing created successfully.')
            return redirect('gigs:my_listings')
    else:
        form = GigListingForm()

    return render(request, 'gigs/create_listing.html', {
        'form': form,
        'venue': venue,
    })


@login_required
def my_listings(request):
    if not (request.user.is_venue_owner() or request.user.is_manager()):
        messages.error(request, 'Only venue owners and managers can view this page.')
        return redirect('gigs:listing_list')

    active_venue_id = request.session.get('active_venue_id')
    if not active_venue_id:
        messages.error(request, 'Please select a venue first.')
        return redirect('venues:dashboard')

    venue = get_object_or_404(Venue, pk=active_venue_id)
    listings = GigListing.objects.filter(venue=venue).order_by('-created_at')

    return render(request, 'gigs/my_listings.html', {
        'listings': listings,
        'venue': venue,
    })


@login_required
def close_listing(request, pk):
    listing = get_object_or_404(GigListing, pk=pk)
    if request.user != listing.created_by and not request.user.is_venue_owner():
        messages.error(request, 'You do not have permission to close this listing.')
        return redirect('gigs:my_listings')
    listing.is_open = False
    listing.save()
    messages.success(request, 'Listing closed successfully.')
    return redirect('gigs:my_listings')