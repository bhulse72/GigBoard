from django.test import TestCase

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from performers.models import CollaborationRequest


class NetworkingTests(TestCase):
    def setUp(self):
        self.performer1 = User.objects.create_user(
            username='djanna',
            password='testpass123',
            role=User.Role.PERFORMER,
            email='djanna@example.com',
            stage_name='DJ Anna',
            music_style='EDM',
            interests='house, remixes',
            location='Notre Dame',
        )

        self.performer2 = User.objects.create_user(
            username='djmike',
            password='testpass123',
            role=User.Role.PERFORMER,
            email='djmike@example.com',
            stage_name='DJ Mike',
            music_style='EDM',
            interests='campus events',
            location='South Bend',
        )

        self.venue_owner = User.objects.create_user(
            username='venue1',
            password='testpass123',
            role=User.Role.VENUE_OWNER,
            email='venue1@example.com',
        )

    def test_collaboration_request_str(self):
        request_obj = CollaborationRequest.objects.create(
            sender=self.performer1,
            receiver=self.performer2,
            message='Want to collaborate?'
        )
        self.assertIn(self.performer1.username, str(request_obj))
        self.assertIn(self.performer2.username, str(request_obj))

    def test_performer_can_view_directory(self):
        self.client.force_login(self.performer1)
        response = self.client.get(reverse('performers:directory'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'DJ Mike')
        self.assertNotContains(response, 'DJ Anna')

    def test_non_performer_cannot_view_directory(self):
        self.client.force_login(self.venue_owner)
        response = self.client.get(reverse('performers:directory'))

        self.assertEqual(response.status_code, 302)

    def test_performer_can_send_collaboration_request(self):
        self.client.force_login(self.performer1)
        response = self.client.post(
            reverse('performers:send_request', args=[self.performer2.id]),
            {'message': 'Want to collaborate next weekend?'},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CollaborationRequest.objects.count(), 1)

        request_obj = CollaborationRequest.objects.first()
        self.assertEqual(request_obj.sender, self.performer1)
        self.assertEqual(request_obj.receiver, self.performer2)
        self.assertEqual(request_obj.status, CollaborationRequest.Status.PENDING)

    def test_duplicate_request_is_not_created(self):
        CollaborationRequest.objects.create(
            sender=self.performer1,
            receiver=self.performer2,
            message='First request'
        )

        self.client.force_login(self.performer1)
        self.client.post(
            reverse('performers:send_request', args=[self.performer2.id]),
            {'message': 'Second request'},
            follow=True,
        )

        self.assertEqual(CollaborationRequest.objects.count(), 1)

    def test_requests_page_shows_incoming_and_outgoing(self):
        CollaborationRequest.objects.create(
            sender=self.performer1,
            receiver=self.performer2,
            message='Let’s collab'
        )

        self.client.force_login(self.performer1)
        response = self.client.get(reverse('performers:requests'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'djmike')
        self.assertContains(response, 'Let’s collab')