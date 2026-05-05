from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from gigs.models import GigApplication
from venues.models import Venue, VenueManager
from .forms import ReviewForm
from .models import Review


def _get_active_venue(request):
    """Return the Venue the current venue owner/manager is acting on behalf of, or None."""
    venue_id = request.session.get('active_venue_id')
    if not venue_id:
        return None
    venue = Venue.objects.filter(pk=venue_id).first()
    if venue is None:
        return None
    if request.user.is_venue_owner() and venue.owner == request.user:
        return venue
    if request.user.is_manager() and VenueManager.objects.filter(user=request.user, venue=venue).exists():
        return venue
    return None


def _verified_app_for_performer_review(user, active_venue, performer):
    """Return a qualifying completed GigApplication for a venue reviewing a performer, or None."""
    return GigApplication.objects.filter(
        listing__venue=active_venue,
        performer=performer,
        status='accepted',
        venue_verified_complete=True,
        performer_verified_complete=True,
    ).first()


def _verified_app_for_venue_review(performer_user, venue):
    """Return a qualifying completed GigApplication for a performer reviewing a venue, or None."""
    return GigApplication.objects.filter(
        listing__venue=venue,
        performer=performer_user,
        status='accepted',
        venue_verified_complete=True,
        performer_verified_complete=True,
    ).first()


@login_required
def submit_performer_review(request, user_id):
    performer = get_object_or_404(User, id=user_id, role='performer')

    if request.user == performer:
        messages.error(request, 'You cannot review yourself.')
        return redirect('performers:profile', user_id=user_id)

    active_venue = None
    qualifying_app = None
    existing_review = None

    if request.user.is_fan():
        reviewer_role = Review.ROLE_FAN
        existing_review = Review.objects.filter(
            reviewer=request.user,
            reviewed_performer=performer,
            reviewing_venue__isnull=True,
        ).first()

    elif request.user.is_performer():
        messages.error(request, 'Performers cannot review other performers.')
        return redirect('performers:profile', user_id=user_id)

    elif request.user.is_venue_owner() or request.user.is_manager():
        active_venue = _get_active_venue(request)
        if not active_venue:
            # Fall back to venue_id posted from the profile page review form
            fallback_id = request.POST.get('venue_id')
            if fallback_id:
                candidate = Venue.objects.filter(pk=fallback_id).first()
                if candidate:
                    authorized = (
                        (request.user.is_venue_owner() and candidate.owner == request.user) or
                        (request.user.is_manager() and VenueManager.objects.filter(
                            user=request.user, venue=candidate).exists())
                    )
                    if authorized:
                        active_venue = candidate
        if not active_venue:
            messages.error(request, 'No active venue selected. Visit your venue management page first.')
            return redirect('performers:profile', user_id=user_id)
        qualifying_app = _verified_app_for_performer_review(request.user, active_venue, performer)
        if not qualifying_app:
            messages.error(request, 'You can only review a performer after completing a verified gig together.')
            return redirect('performers:profile', user_id=user_id)
        reviewer_role = Review.ROLE_VENUE
        existing_review = Review.objects.filter(
            reviewing_venue=active_venue,
            reviewed_performer=performer,
        ).first()

    else:
        return redirect('performers:profile', user_id=user_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewer_role = reviewer_role
            review.reviewed_performer = performer
            review.reviewing_venue = active_venue
            review.related_application = qualifying_app
            if existing_review:
                review.is_edited = True
            review.save()
            messages.success(request, 'Review saved.')
            return redirect('performers:profile', user_id=user_id)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'subject_name': performer.stage_name or performer.username,
        'subject_type': 'performer',
        'existing_review': existing_review,
    })


@login_required
def submit_venue_review(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    qualifying_app = None
    existing_review = None

    if request.user.is_fan():
        reviewer_role = Review.ROLE_FAN
        existing_review = Review.objects.filter(
            reviewer=request.user,
            reviewed_venue=venue,
        ).first()

    elif request.user.is_performer():
        qualifying_app = _verified_app_for_venue_review(request.user, venue)
        if not qualifying_app:
            messages.error(request, 'You can only review a venue after completing a verified gig there.')
            return redirect('venues:detail', pk=venue_id)
        reviewer_role = Review.ROLE_PERFORMER
        existing_review = Review.objects.filter(
            reviewer=request.user,
            reviewed_venue=venue,
        ).first()

    elif request.user.is_venue_owner() or request.user.is_manager():
        messages.error(request, 'Venues cannot review other venues.')
        return redirect('venues:detail', pk=venue_id)

    else:
        return redirect('venues:detail', pk=venue_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.reviewer_role = reviewer_role
            review.reviewed_venue = venue
            review.related_application = qualifying_app
            if existing_review:
                review.is_edited = True
            review.save()
            messages.success(request, 'Review saved.')
            return redirect('venues:detail', pk=venue_id)
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'reviews/review_form.html', {
        'form': form,
        'subject_name': venue.name,
        'subject_type': 'venue',
        'existing_review': existing_review,
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    is_owner = review.reviewer == request.user
    is_venue_owner = (
        review.reviewing_venue is not None and (
            (request.user.is_venue_owner() and review.reviewing_venue.owner == request.user) or
            (request.user.is_manager() and VenueManager.objects.filter(
                user=request.user, venue=review.reviewing_venue
            ).exists())
        )
    )

    if not (is_owner or is_venue_owner):
        messages.error(request, 'You do not have permission to delete this review.')
        return redirect('accounts:profile')

    if request.method == 'POST':
        if review.reviewed_performer:
            target_url = redirect('performers:profile', user_id=review.reviewed_performer_id)
        else:
            target_url = redirect('venues:detail', pk=review.reviewed_venue_id)
        review.delete()
        messages.success(request, 'Review deleted.')
        return target_url

    return redirect('accounts:profile')
