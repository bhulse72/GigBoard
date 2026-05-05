from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_notification_gig_invite'),
        ('notifications', '0002_copy_data'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
