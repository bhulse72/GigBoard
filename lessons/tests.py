from django.test import TestCase, Client
from datetime import date, time
from django.urls import reverse
from accounts.models import User
from lessons.models import LessonListing, TimeSlot, Booking
from django.utils.formats import date_format



class LessonsTestSetup(TestCase):
    """Base setup shared across test cases."""

    def setUp(self):
        self.client = Client()

        self.instructor = User.objects.create_user(
            username='instructor1',
            password='testpass123',
            role='performer',
            location='Chicago, IL',
        )
        self.student = User.objects.create_user(
            username='student1',
            password='testpass123',
            role='performer',
            location='Nashville, TN',
        )
        self.venue_owner = User.objects.create_user(
            username='venueowner1',
            password='testpass123',
            role='venue_owner',
        )

        self.listing = LessonListing.objects.create(
            instructor=self.instructor,
            title='Intro to Guitar',
            description='Learn basic chords and strumming.',
            style='guitar',
            price=50.00,
            duration_minutes=60,
            format='in_person',
            location='Chicago, IL',
            is_active=True,
        )

        self.slot = TimeSlot.objects.create(
            listing=self.listing,
            date=date(2026, 6, 1),
            start_time=time(14, 0),
            is_booked=False,
        )


class LessonListingModelTest(LessonsTestSetup):

    def test_listing_str(self):
        self.assertIn('Intro to Guitar', str(self.listing))
        self.assertIn('instructor1', str(self.listing))

    def test_slot_str(self):
        self.assertIn('Intro to Guitar', str(self.slot))

    def test_listing_is_active_by_default(self):
        self.assertTrue(self.listing.is_active)

    def test_slot_is_not_booked_by_default(self):
        self.assertFalse(self.slot.is_booked)


class LessonListingListViewTest(LessonsTestSetup):

    def test_listing_list_accessible_when_logged_in(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_list'))
        self.assertEqual(response.status_code, 200)

    def test_listing_list_shows_active_listings(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_list'))
        self.assertContains(response, 'Intro to Guitar')

    def test_listing_list_does_not_show_inactive(self):
        self.listing.is_active = False
        self.listing.save()
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_list'))
        self.assertNotContains(response, 'Intro to Guitar')

    def test_listing_list_filter_by_style(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_list') + '?style=guitar')
        self.assertContains(response, 'Intro to Guitar')

    def test_listing_list_filter_excludes_wrong_style(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_list') + '?style=drums')
        self.assertNotContains(response, 'Intro to Guitar')


class CreateListingViewTest(LessonsTestSetup):

    def test_performer_can_access_create_page(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.get(reverse('lessons:create_listing'))
        self.assertEqual(response.status_code, 200)

    def test_non_performer_cannot_create_listing(self):
        self.client.login(username='venueowner1', password='testpass123')
        response = self.client.get(reverse('lessons:create_listing'))
        self.assertRedirects(response, reverse('lessons:listing_list'))

    def test_performer_can_create_listing(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.post(reverse('lessons:create_listing'), {
            'title': 'Advanced Drums',
            'description': 'For experienced players.',
            'style': 'drums',
            'price': '75.00',
            'duration_minutes': 90,
            'format': 'online',
            'location': 'Remote',
        })
        self.assertRedirects(response, reverse('lessons:my_listings'))
        self.assertTrue(LessonListing.objects.filter(title='Advanced Drums').exists())

    def test_create_listing_requires_login(self):
        response = self.client.get(reverse('lessons:create_listing'))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('lessons:create_listing')}")


class ListingDetailViewTest(LessonsTestSetup):

    def test_detail_page_loads(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_detail', args=[self.listing.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intro to Guitar')

    def test_detail_shows_available_slots(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_detail', args=[self.listing.pk]))

        formatted_date = date_format(self.slot.date)
        self.assertContains(response, formatted_date)


    def test_instructor_sees_add_slot_form(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_detail', args=[self.listing.pk]))
        self.assertContains(response, 'Add Available Time Slot')

    def test_student_does_not_see_add_slot_form(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:listing_detail', args=[self.listing.pk]))
        self.assertNotContains(response, 'Add Available Time Slot')


class AddSlotViewTest(LessonsTestSetup):

    def test_instructor_can_add_slot(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.post(reverse('lessons:add_slot', args=[self.listing.pk]), {
            'date': '2026-07-01',
            'start_time': '10:00',
        })
        self.assertRedirects(response, reverse('lessons:listing_detail', args=[self.listing.pk]))
        self.assertEqual(self.listing.time_slots.count(), 2)

    def test_non_instructor_cannot_add_slot(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.post(reverse('lessons:add_slot', args=[self.listing.pk]), {
            'date': '2026-07-01',
            'start_time': '10:00',
        })
        self.assertEqual(response.status_code, 404)


class BookSlotViewTest(LessonsTestSetup):

    def test_student_can_view_booking_page(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:book_slot', args=[self.listing.pk, self.slot.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Confirm Booking')

    def test_student_can_book_slot(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.post(reverse('lessons:book_slot', args=[self.listing.pk, self.slot.pk]), {
            'note': 'Looking forward to it!',
        })
        self.assertRedirects(response, reverse('lessons:my_bookings'))
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)
        self.assertTrue(Booking.objects.filter(student=self.student, slot=self.slot).exists())

    def test_instructor_cannot_book_own_slot(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.post(reverse('lessons:book_slot', args=[self.listing.pk, self.slot.pk]), {
            'note': '',
        })
        self.assertRedirects(response, reverse('lessons:listing_detail', args=[self.listing.pk]))
        self.assertFalse(Booking.objects.filter(slot=self.slot).exists())

    def test_already_booked_slot_returns_404(self):
        self.slot.is_booked = True
        self.slot.save()
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:book_slot', args=[self.listing.pk, self.slot.pk]))
        self.assertEqual(response.status_code, 404)

    def test_booking_requires_login(self):
        response = self.client.get(reverse('lessons:book_slot', args=[self.listing.pk, self.slot.pk]))
        self.assertEqual(response.status_code, 302)


class MyListingsViewTest(LessonsTestSetup):

    def test_performer_can_view_my_listings(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.get(reverse('lessons:my_listings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intro to Guitar')

    def test_non_performer_redirected(self):
        self.client.login(username='venueowner1', password='testpass123')
        response = self.client.get(reverse('lessons:my_listings'))
        self.assertRedirects(response, reverse('lessons:listing_list'))

    def test_only_own_listings_shown(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:my_listings'))
        self.assertNotContains(response, 'Intro to Guitar')


class MyBookingsViewTest(LessonsTestSetup):

    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            student=self.student,
            slot=self.slot,
            note='Excited to learn!',
        )
        self.slot.is_booked = True
        self.slot.save()

    def test_student_can_view_bookings(self):
        self.client.login(username='student1', password='testpass123')
        response = self.client.get(reverse('lessons:my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Intro to Guitar')

    def test_booking_requires_login(self):
        response = self.client.get(reverse('lessons:my_bookings'))
        self.assertEqual(response.status_code, 302)

    def test_only_own_bookings_shown(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.get(reverse('lessons:my_bookings'))
        self.assertNotContains(response, 'Intro to Guitar')


class MyStudentsViewTest(LessonsTestSetup):

    def setUp(self):
        super().setUp()
        self.booking = Booking.objects.create(
            student=self.student,
            slot=self.slot,
            note='Ready to learn!',
        )
        self.slot.is_booked = True
        self.slot.save()

    def test_instructor_can_view_students(self):
        self.client.login(username='instructor1', password='testpass123')
        response = self.client.get(reverse('lessons:my_students'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'student1')

    def test_non_performer_redirected(self):
        self.client.login(username='venueowner1', password='testpass123')
        response = self.client.get(reverse('lessons:my_students'))
        self.assertRedirects(response, reverse('lessons:listing_list'))