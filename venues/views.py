from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Venue, VenueManager
from .forms import VenueForm
from gigs.models import GigListing, GigApplication
from reviews.models import Review
from reviews.forms import ReviewForm


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
    for venue in venues:
        venue.genre_tag_list = [tag.strip() for tag in venue.genre_tags.split(',')] if venue.genre_tags else []
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
    from django.utils import timezone
    venue = get_object_or_404(Venue, pk=pk)
    if not can_manage_venue(request.user, venue):
        messages.error(request, 'You do not have access to that venue.')
        return redirect('venues:dashboard')
    request.session['active_venue_id'] = venue.pk
    request.session['active_venue_name'] = venue.name
    today = timezone.now().date()
    gig_listings = GigListing.objects.filter(venue=venue).order_by('-event_date')
    past_gigs = GigApplication.objects.filter(
        listing__venue=venue,
        status='accepted',
        listing__event_date__lt=today,
    ).select_related('listing', 'performer').order_by('-listing__event_date')
    genre_tags = venue.genre_tags.split(',') if venue.genre_tags else []

    return render(request, 'venues/manage.html', {
        'venue': venue,
        'gig_listings': gig_listings,
        'past_gigs': past_gigs,
        'genre_tags': genre_tags,
    })


@login_required
def venue_browser(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can browse venues.')
        return redirect('accounts:profile')

    venues = Venue.objects.all()

    location = request.GET.get('location', '').strip()
    genre = request.GET.get('genre', '').strip()
    open_only = request.GET.get('open_only', '')

    if location:
        venues = venues.filter(city__icontains=location) | venues.filter(state__icontains=location)
    if genre:
        venues = venues.filter(genre_tags__icontains=genre)
    if open_only:
        venues = venues.filter(gig_listings__is_open=True).distinct()

    venues = venues.order_by('name')

    return render(request, 'venues/browse.html', {
        'venues': venues,
        'location': location,
        'genre': genre,
        'open_only': open_only,
    })


@login_required
def venue_detail(request, pk):
    venue = get_object_or_404(Venue, pk=pk)
    open_listings = GigListing.objects.filter(venue=venue, is_open=True).order_by('event_date')

    user_applications = {}
    if request.user.is_performer():
        apps = GigApplication.objects.filter(
            performer=request.user,
            listing__in=open_listings
        ).values_list('listing_id', 'status')
        user_applications = dict(apps)

    # Reviews
    reviews = Review.objects.filter(
        reviewed_venue=venue
    ).select_related('reviewer', 'reviewing_venue').order_by('-created_at')

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    can_review = False
    existing_review = None
    review_form = None

    if request.user.is_fan():
        can_review = True
        existing_review = Review.objects.filter(
            reviewer=request.user,
            reviewed_venue=venue,
        ).first()

    elif request.user.is_performer():
        has_completed_gig = GigApplication.objects.filter(
            listing__venue=venue,
            performer=request.user,
            status='accepted',
            venue_verified_complete=True,
            performer_verified_complete=True,
        ).exists()
        if has_completed_gig:
            can_review = True
            existing_review = Review.objects.filter(
                reviewer=request.user,
                reviewed_venue=venue,
            ).first()

    if can_review:
        review_form = ReviewForm(instance=existing_review)

    return render(request, 'venues/detail.html', {
        'venue': venue,
        'open_listings': open_listings,
        'user_applications': user_applications,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'can_review': can_review,
        'existing_review': existing_review,
        'review_form': review_form,
    })