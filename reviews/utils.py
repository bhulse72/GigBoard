# Notification logic has moved to notifications/service.py.
# This shim keeps existing imports working during the transition.
from notifications.service import generate_gig_notifications  # noqa: F401
