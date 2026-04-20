from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import EditProfileForm

@login_required
def profile(request):
    context = {}
    if request.user.is_performer():
        from gigs.models import GigApplication
        today = timezone.now().date()
        accepted = GigApplication.objects.filter(
            performer=request.user, status='accepted'
        ).select_related('listing').order_by('listing__event_date')
        context['upcoming_gigs'] = [a for a in accepted if a.listing.event_date >= today]
        context['past_gigs'] = [a for a in accepted if a.listing.event_date < today]
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