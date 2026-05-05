from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_reset_sequence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(
                choices=[
                    ('verify_gig', 'Verify Gig Completion'),
                    ('leave_review', 'Leave a Review'),
                    ('gig_invite', 'Gig Invitation'),
                    ('application_accepted', 'Application Accepted'),
                    ('application_declined', 'Application Declined'),
                ],
                max_length=30,
            ),
        ),
    ]
