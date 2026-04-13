from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from .forms import CollaborationRequestForm
from .models import CollaborationRequest


@login_required
def performer_directory(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can access the networking directory.')
        return redirect('accounts:profile')

    performers = User.objects.filter(role='performer').exclude(id=request.user.id)

    if request.user.music_style:
        similar_performers = performers.filter(music_style=request.user.music_style)
    else:
        similar_performers = performers

    return render(request, 'performers/directory.html', {
        'performers': similar_performers,
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