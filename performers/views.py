from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from accounts.models import User
from gigs.models import GigApplication
from reviews.models import Review
from reviews.forms import ReviewForm
from .forms import CollaborationRequestForm
from .models import CollaborationRequest


@login_required
def performer_directory(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can access the networking directory.')
        return redirect('accounts:profile')

    from django.db.models import Avg, Case, When, IntegerField

    performers = User.objects.filter(role='performer').exclude(id=request.user.id).annotate(
        avg_rating=Avg('reviews_received__rating')
    )

    if request.user.music_style:
        performers = performers.annotate(
            is_similar=Case(
                When(music_style=request.user.music_style, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by('is_similar', 'username')
    else:
        performers = performers.order_by('username')

    return render(request, 'performers/directory.html', {
        'performers': performers,
        'user_style': request.user.music_style,
    })


@login_required
def send_collab_request(request, user_id):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can send collaboration requests.')
        return redirect('accounts:profile')

    receiver = get_object_or_404(User, id=user_id, role='performer')

    if receiver == request.user:
        messages.error(request, 'You cannot send a collaboration request to yourself.')
        return redirect('performers:directory')

    existing = CollaborationRequest.objects.filter(
        sender=request.user,
        receiver=receiver
    ).first()

    if existing:
        messages.info(request, 'You already sent a request to this performer.')
        return redirect('performers:directory')

    if request.method == 'POST':
        form = CollaborationRequestForm(request.POST)
        if form.is_valid():
            collab_request = form.save(commit=False)
            collab_request.sender = request.user
            collab_request.receiver = receiver
            collab_request.save()
            messages.success(request, 'Collaboration request sent.')
            return redirect('performers:requests')
    else:
        form = CollaborationRequestForm()

    return render(request, 'performers/send_request.html', {
        'form': form,
        'receiver': receiver,
    })


@login_required
def performer_browser(request):
    if not (request.user.is_venue_owner() or request.user.is_manager()):
        messages.error(request, 'Only venue owners and managers can browse performers.')
        return redirect('accounts:profile')

    from django.db.models import Avg

    performers = User.objects.filter(role='performer').annotate(
        avg_rating=Avg('reviews_received__rating')
    )

    location = request.GET.get('location', '').strip()
    style = request.GET.get('style', '').strip()
    name = request.GET.get('name', '').strip()

    if name:
        performers = performers.filter(
            models.Q(stage_name__icontains=name) |
            models.Q(first_name__icontains=name) |
            models.Q(last_name__icontains=name) |
            models.Q(username__icontains=name)
        )
    if location:
        performers = performers.filter(location__icontains=location)
    if style:
        performers = performers.filter(music_style__icontains=style)

    return render(request, 'performers/browse.html', {
        'performers': performers,
        'location': location,
        'style': style,
        'name': name,
    })


@login_required
def performer_profile(request, user_id):
    from django.db.models import Avg
    from venues.models import Venue

    performer = get_object_or_404(User, id=user_id, role='performer')
    today = timezone.now().date()

    accepted_gigs = GigApplication.objects.filter(
        performer=performer, status='accepted'
    ).select_related('listing').order_by('listing__event_date')

    upcoming_gigs = [a for a in accepted_gigs if a.listing.event_date >= today]
    past_gigs = [a for a in accepted_gigs if a.listing.event_date < today]

    already_sent = False
    if request.user.is_performer() and request.user != performer:
        already_sent = CollaborationRequest.objects.filter(
            sender=request.user, receiver=performer
        ).exists()

    # Reviews
    reviews = Review.objects.filter(
        reviewed_performer=performer
    ).select_related('reviewer', 'reviewing_venue').order_by('-created_at')

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']

    # Determine if the current user can leave / already has a review
    can_review = False
    existing_review = None
    review_form = None

    if request.user != performer:
        if request.user.is_fan():
            can_review = True
            existing_review = Review.objects.filter(
                reviewer=request.user,
                reviewed_performer=performer,
                reviewing_venue__isnull=True,
            ).first()

        elif request.user.is_venue_owner() or request.user.is_manager():
            # Try session first, then auto-detect a qualifying venue for this performer
            active_venue_id = request.session.get('active_venue_id')
            active_venue = Venue.objects.filter(pk=active_venue_id).first() if active_venue_id else None

            if not active_venue:
                if request.user.is_venue_owner():
                    candidate_venues = Venue.objects.filter(owner=request.user)
                else:
                    candidate_venues = Venue.objects.filter(venuemanager__user=request.user)

                active_venue = candidate_venues.filter(
                    gig_listings__applications__performer=performer,
                    gig_listings__applications__status='accepted',
                    gig_listings__applications__venue_verified_complete=True,
                    gig_listings__applications__performer_verified_complete=True,
                ).first()

            if active_venue:
                has_completed_gig = GigApplication.objects.filter(
                    listing__venue=active_venue,
                    performer=performer,
                    status='accepted',
                    venue_verified_complete=True,
                    performer_verified_complete=True,
                ).exists()
                if has_completed_gig:
                    can_review = True
                    existing_review = Review.objects.filter(
                        reviewing_venue=active_venue,
                        reviewed_performer=performer,
                    ).first()

        if can_review:
            review_form = ReviewForm(instance=existing_review)

    return render(request, 'performers/profile.html', {
        'performer': performer,
        'upcoming_gigs': upcoming_gigs,
        'past_gigs': past_gigs,
        'already_sent': already_sent,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'can_review': can_review,
        'existing_review': existing_review,
        'review_form': review_form,
        'review_venue': active_venue if can_review else None,
    })


@login_required
def connections_feed(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can access the network feed.')
        return redirect('accounts:profile')

    from django.db.models import Q

    connected_ids = list(
        CollaborationRequest.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            status=CollaborationRequest.Status.ACCEPTED,
        ).values_list('receiver_id', flat=True).filter(sender=request.user)
    ) + list(
        CollaborationRequest.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            status=CollaborationRequest.Status.ACCEPTED,
        ).values_list('sender_id', flat=True).filter(receiver=request.user)
    )

    today = timezone.now().date()

    gig_apps = GigApplication.objects.filter(
        performer_id__in=connected_ids,
        status='accepted',
    ).select_related('listing', 'performer').order_by('listing__event_date')

    upcoming = [a for a in gig_apps if a.listing.event_date >= today]
    past = sorted(
        [a for a in gig_apps if a.listing.event_date < today],
        key=lambda a: a.listing.event_date,
        reverse=True,
    )

    return render(request, 'performers/feed.html', {
        'upcoming': upcoming,
        'past': past,
        'has_connections': bool(connected_ids),
    })


@login_required
def my_connections(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can access connections.')
        return redirect('accounts:profile')

    from django.db.models import Avg, Q

    accepted = CollaborationRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status=CollaborationRequest.Status.ACCEPTED,
    )
    sender_ids = accepted.filter(receiver=request.user).values_list('sender_id', flat=True)
    receiver_ids = accepted.filter(sender=request.user).values_list('receiver_id', flat=True)
    connected_ids = list(sender_ids) + list(receiver_ids)

    connections = User.objects.filter(id__in=connected_ids).annotate(
        avg_rating=Avg('reviews_received__rating')
    )

    query = request.GET.get('q', '').strip()
    if query:
        connections = connections.filter(
            models.Q(stage_name__icontains=query) |
            models.Q(first_name__icontains=query) |
            models.Q(last_name__icontains=query) |
            models.Q(username__icontains=query) |
            models.Q(music_style__icontains=query)
        )

    return render(request, 'performers/connections.html', {
        'connections': connections,
        'query': query,
    })


@login_required
def my_requests(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can access collaboration requests.')
        return redirect('accounts:profile')

    incoming_requests = CollaborationRequest.objects.filter(receiver=request.user).order_by('-created_at')
    outgoing_requests = CollaborationRequest.objects.filter(sender=request.user).order_by('-created_at')

    return render(request, 'performers/requests.html', {
        'incoming_requests': incoming_requests,
        'outgoing_requests': outgoing_requests,
    })

@login_required
def accept_collab_request(request, request_id):
    collab_request = get_object_or_404(
        CollaborationRequest,
        id=request_id,
        receiver=request.user,
    )

    if request.method == 'POST':
        if collab_request.status == CollaborationRequest.Status.PENDING:
            collab_request.status = CollaborationRequest.Status.ACCEPTED
            collab_request.save()
            messages.success(request, 'Collaboration request accepted.')

    return redirect('performers:requests')

@login_required
def decline_collab_request(request, request_id):
    collab_request = get_object_or_404(
        CollaborationRequest,
        id=request_id,
        receiver=request.user,
    )

    if request.method == 'POST':
        if collab_request.status == CollaborationRequest.Status.PENDING:
            collab_request.status = CollaborationRequest.Status.DECLINED
            collab_request.save()
            messages.success(request, 'Collaboration request declined.')
    
    return redirect('performers:requests')
