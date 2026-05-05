from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0004_application_notification_types'),
        ('performers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='related_collab_request',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='notifications',
                to='performers.collaborationrequest',
            ),
        ),
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
                    ('collab_request_received', 'Collaboration Request Received'),
                    ('collab_request_accepted', 'Collaboration Request Accepted'),
                    ('collab_request_declined', 'Collaboration Request Declined'),
                ],
                max_length=30,
            ),
        ),
    ]
