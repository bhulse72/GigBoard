from .models import LessonListing, TimeSlot, Booking
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LessonListingForm, TimeSlotForm


def listing_list(request):
    listings = LessonListing.objects.filter(is_active=True).order_by('-created_at')

    style = request.GET.get('style')
    if style:
        listings = listings.filter(style=style)

    format_filter = request.GET.get('format')
    if format_filter:
        listings = listings.filter(format=format_filter)

    return render(request, 'lessons/listing_list.html', {
        'listings': listings,
        'style_choices': LessonListing.STYLE_CHOICES,
        'format_choices': LessonListing.FORMAT_CHOICES,
        'selected_style': style,
        'selected_format': format_filter,
    })


@login_required
def create_listing(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can offer lessons.')
        return redirect('lessons:listing_list')

    if request.method == 'POST':
        form = LessonListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.instructor = request.user
            listing.save()
            messages.success(request, 'Lesson listing created!')
            return redirect('lessons:my_listings')
    else:
        form = LessonListingForm()

    return render(request, 'lessons/create_listing.html', {'form': form})


@login_required
def my_listings(request):
    if not request.user.is_performer():
        messages.error(request, 'Only performers can view this page.')
        return redirect('lessons:listing_list')

    listings = LessonListing.objects.filter(instructor=request.user).order_by('-created_at')
    return render(request, 'lessons/my_listings.html', {'listings': listings})


def listing_detail(request, pk):
    listing = get_object_or_404(LessonListing, pk=pk, is_active=True)
    available_slots = listing.time_slots.filter(is_booked=False)

    slot_form = None
    if request.user.is_authenticated and request.user == listing.instructor:
        slot_form = TimeSlotForm()

    return render(request, 'lessons/listing_detail.html', {
        'listing': listing,
        'available_slots': available_slots,
        'slot_form': slot_form,
    })


@login_required
def add_slot(request, pk):
    listing = get_object_or_404(LessonListing, pk=pk, instructor=request.user)

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            slot = form.save(commit=False)
            slot.listing = listing
            slot.save()
            messages.success(request, 'Time slot added.')
        else:
            messages.error(request, 'Invalid slot data.')

    return redirect('lessons:listing_detail', pk=pk)


@login_required
def book_slot(request, pk, slot_pk):
    listing = get_object_or_404(LessonListing, pk=pk)
    slot = get_object_or_404(TimeSlot, pk=slot_pk, listing=listing, is_booked=False)

    if request.user == listing.instructor:
        messages.error(request, 'You cannot book your own lesson.')
        return redirect('lessons:listing_detail', pk=pk)

    if request.method == 'POST':
        note = request.POST.get('note', '')
        Booking.objects.create(student=request.user, slot=slot, note=note)
        slot.is_booked = True
        slot.save()
        messages.success(request, f'Lesson booked for {slot.date} at {slot.start_time}!')
        return redirect('lessons:my_bookings')

    return render(request, 'lessons/book_slot.html', {
        'listing': listing,
        'slot': slot,
    })


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(student=request.user).select_related('slot__listing').order_by('slot__date')
    return render(request, 'lessons/my_bookings.html', {'bookings': bookings})

@login_required
def my_students(request):
    if not request.user.is_performer():
        return redirect('lessons:listing_list')
    
    bookings = Booking.objects.filter(
        slot__listing__instructor=request.user
    ).select_related('slot__listing', 'student').order_by('slot__date')
    
    return render(request, 'lessons/my_students.html', {'bookings': bookings})