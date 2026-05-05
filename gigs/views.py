import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import GigListing, GigApplication
from .forms import GigListingForm
from venues.models import Venue, VenueManager
from accounts.models import User


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

    venues = Venue.objects.filter(owner=request.user)
    active_venue_id = request.session.get('active_venue_id')

    if request.method == 'POST':
        form = GigListingForm(request.POST)
        venue_id = request.POST.get('venue_id')
        venue = get_object_or_404(Venue, pk=venue_id, owner=request.user)
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
        venue = get_object_or_404(Venue, pk=active_venue_id) if active_venue_id else None

    return render(request, 'gigs/create_listing.html', {
        'form': form,
        'venues': venues,
        'active_venue': venue,
    })


@login_required
def my_listings(request):
    if not (request.user.is_venue_owner() or request.user.is_manager()):
        messages.error(request, 'Only venue owners and managers can view this page.')
        return redirect('gigs:listing_list')

    active_venue_id = request.session.get('active_venue_id')
    listings = GigListing.objects.filter(created_by=request.user).order_by('-created_at')

    return render(request, 'gigs/my_listings.html', {
        'listings': listings,
        'active_venue_id': active_venue_id,
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


@login_required
def apply_to_gig(request, pk):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can apply to gigs.')
        return redirect('gigs:listing_list')

    listing = get_object_or_404(GigListing, pk=pk, is_open=True)

    if GigApplication.objects.filter(listing=listing, performer=request.user).exists():
        messages.info(request, 'You have already applied to this gig.')
        return redirect('gigs:listing_list')

    if request.method == 'POST':
        message = request.POST.get('message', '')
        GigApplication.objects.create(listing=listing, performer=request.user, message=message)
        messages.success(request, 'Application submitted!')
        return redirect('gigs:listing_list')

    return render(request, 'gigs/apply.html', {'listing': listing})


@login_required
def listing_applications(request, pk):
    listing = get_object_or_404(GigListing, pk=pk, created_by=request.user)
    applications = listing.applications.select_related('performer').order_by('created_at')
    return render(request, 'gigs/applications.html', {
        'listing': listing,
        'applications': applications,
    })


@login_required
def update_application(request, pk):
    application = get_object_or_404(GigApplication, pk=pk, listing__created_by=request.user)
    new_status = request.POST.get('status')
    if new_status in ('accepted', 'declined'):
        application.status = new_status
        application.save()
        messages.success(request, f'Application {new_status}.')
    return redirect('gigs:listing_applications', pk=application.listing.pk)


@login_required
def verify_gig_completion(request, pk):
    if request.method != 'POST':
        return redirect('accounts:profile')

    app = get_object_or_404(GigApplication, pk=pk)
    today = timezone.now().date()

    if app.listing.event_date >= today:
        messages.error(request, 'This gig has not yet taken place.')
    elif request.user.is_performer() and app.performer == request.user:
        if not app.performer_verified_complete:
            app.performer_verified_complete = True
            app.save()
            messages.success(request, 'Gig marked as complete on your end.')
        else:
            messages.info(request, 'You have already verified this gig.')
    elif request.user.is_venue_owner() or request.user.is_manager():
        can_verify = (
            (request.user.is_venue_owner() and app.listing.venue and app.listing.venue.owner == request.user) or
            (request.user.is_manager() and VenueManager.objects.filter(user=request.user, venue=app.listing.venue).exists())
        )
        if can_verify:
            if not app.venue_verified_complete:
                app.venue_verified_complete = True
                app.save()
                messages.success(request, 'Gig marked as complete.')
            else:
                messages.info(request, 'You have already verified this gig.')
        else:
            messages.error(request, 'You do not have permission to verify this gig.')
    else:
        messages.error(request, 'You do not have permission to verify this gig.')

    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('accounts:profile')


@login_required
def invite_performer(request, performer_id):
    if not (request.user.is_venue_owner() or request.user.is_manager()):
        messages.error(request, 'Only venue owners and managers can invite performers.')
        return redirect('accounts:profile')

    performer = get_object_or_404(User, id=performer_id, role='performer')

    # Gather open listings belonging to this user
    open_listings = GigListing.objects.filter(created_by=request.user, is_open=True).order_by('event_date')

    if not open_listings.exists():
        messages.error(request, 'You have no open gig listings to invite performers to.')
        return redirect('performers:browse')

    if request.method == 'POST':
        from reviews.models import Notification

        listing_id = request.POST.get('listing_id')
        listing = get_object_or_404(GigListing, pk=listing_id, created_by=request.user, is_open=True)

        already_invited = Notification.objects.filter(
            recipient=performer,
            notification_type=Notification.GIG_INVITE,
            related_listing=listing,
        ).exists()

        if already_invited:
            messages.info(request, f'{performer.stage_name or performer.username} has already been invited to that gig.')
            return redirect('performers:browse')

        venue_display = listing.venue_name or request.user.username
        Notification.objects.create(
            recipient=performer,
            notification_type=Notification.GIG_INVITE,
            related_listing=listing,
            message=(
                f'{venue_display} has invited you to apply for "{listing.title}" '
                f'on {listing.event_date.strftime("%B %-d, %Y")}.'
            ),
        )
        messages.success(request, f'Invitation sent to {performer.stage_name or performer.username}.')
        return redirect('performers:browse')

    return render(request, 'gigs/invite_performer.html', {
        'performer': performer,
        'open_listings': open_listings,
    })


@login_required
def calendar_view(request):
    return render(request, 'gigs/calendar.html')


@login_required
def calendar_events(request):
    events = []

    if request.user.is_venue_owner() or request.user.is_manager():
        listings = GigListing.objects.filter(created_by=request.user)
        for listing in listings:
            accepted = listing.applications.filter(status='accepted').first()
            events.append({
                'title': listing.title,
                'start': f"{listing.event_date}T{listing.start_time}",
                'color': '#4f46e5' if listing.is_open else '#6b7280',
                'extendedProps': {
                    'venue': listing.venue_name,
                    'pay': str(listing.pay),
                    'style': listing.get_preferred_style_display(),
                    'status': 'Open' if listing.is_open else 'Closed',
                    'performer': str(accepted.performer) if accepted else 'No performer yet',
                },
            })

    elif request.user.is_performer():
        applications = GigApplication.objects.filter(
            performer=request.user,
            status='accepted',
        ).select_related('listing')
        for app in applications:
            listing = app.listing
            events.append({
                'title': listing.title,
                'start': f"{listing.event_date}T{listing.start_time}",
                'color': '#059669',
                'extendedProps': {
                    'venue': listing.venue_name,
                    'pay': str(listing.pay),
                    'style': listing.get_preferred_style_display(),
                },
            })

    return JsonResponse(events, safe=False)