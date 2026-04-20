from django.urls import reverse
from performers.models import CollaborationRequest

def test_receiver_can_accept_request(self):
    collab_request = CollaborationRequest.objects.create(
        sender=self.performer1,
        receiver=self.performer2,
        message='Let’s collab'
    )

    self.client.force_login(self.performer2)
    response = self.client.post(
        reverse('performers:accept_request', args=[collab_request.id]),
        follow=True,
    )

    self.assertEqual(response.status_code, 200)
    collab_request.refresh_from_db()
    self.assertEqual(collab_request.status, CollaborationRequest.Status.ACCEPTED)


def test_receiver_can_decline_request(self):
    collab_request = CollaborationRequest.objects.create(
        sender=self.performer1,
        receiver=self.performer2,
        message='Let’s collab'
    )

    self.client.force_login(self.performer2)
    response = self.client.post(
        reverse('performers:decline_request', args=[collab_request.id]),
        follow=True,
    )

    self.assertEqual(response.status_code, 200)
    collab_request.refresh_from_db()
    self.assertEqual(collab_request.status, CollaborationRequest.Status.DECLINED)


def test_sender_cannot_accept_request(self):
    collab_request = CollaborationRequest.objects.create(
        sender=self.performer1,
        receiver=self.performer2,
        message='Let’s collab'
    )

    self.client.force_login(self.performer1)
    response = self.client.post(
        reverse('performers:accept_request', args=[collab_request.id]),
    )

    self.assertEqual(response.status_code, 404)