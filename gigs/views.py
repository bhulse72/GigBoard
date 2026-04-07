from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import GigListing
from .forms import GigListingForm 

# Create your views here.

@login_required
def listing_list(request):
    listings = GigListing.objects.filter(is_open=True).order_by('event_date', 'start_time')
    return render(request, 'gigs/listing_list.html', {'listings': listings})

@login_required
def create_listing(request):
    if not request.user.is_venue_owner():
        messages.error(request, 'Only venue owners can create listings.')
        return redirect('gigs:listing_list')

    if request.method == 'POST':
        form = GigListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.created_by = request.user
            listing.save()
            messages.success(request, 'Gig listing created successfully.')
            return redirect('gigs:my_listings')
    else:
        form = GigListingForm()

    return render(request, 'gigs/create_listing.html', {'form': form})

@login_required
def my_listings(request):
    if not request.user.is_venue_owner():
        messages.error(request, 'Only venue owners can view this page.')
        return redirect('gigs:listing_list')

    listings = GigListing.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'gigs/my_listings.html', {'listings': listings})