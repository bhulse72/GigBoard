from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_add_notification'),
        ('gigs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='related_listing',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='invite_notifications',
                to='gigs.giglisting',
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
                ],
                max_length=30,
            ),
        ),
    ]
