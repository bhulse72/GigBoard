from django.db import migrations


def copy_notifications(apps, schema_editor):
    OldNotification = apps.get_model('reviews', 'Notification')
    NewNotification = apps.get_model('notifications', 'Notification')

    for old in OldNotification.objects.all():
        NewNotification.objects.get_or_create(
            id=old.id,
            defaults=dict(
                recipient_id=old.recipient_id,
                notification_type=old.notification_type,
                message=old.message,
                is_read=old.is_read,
                related_application_id=old.related_application_id,
                related_listing_id=old.related_listing_id,
                created_at=old.created_at,
            ),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(copy_notifications, migrations.RunPython.noop),
    ]
