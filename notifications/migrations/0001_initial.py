from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gigs', '0001_initial'),
        ('reviews', '0003_notification_gig_invite'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(
                    choices=[
                        ('verify_gig', 'Verify Gig Completion'),
                        ('leave_review', 'Leave a Review'),
                        ('gig_invite', 'Gig Invitation'),
                    ],
                    max_length=30,
                )),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to=settings.AUTH_USER_MODEL,
                )),
                ('related_application', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notifications',
                    to='gigs.gigapplication',
                )),
                ('related_listing', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='invite_notifications',
                    to='gigs.giglisting',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='notification',
            constraint=models.UniqueConstraint(
                fields=['recipient', 'notification_type', 'related_application'],
                name='notifications_unique_recipient_type_application',
            ),
        ),
    ]
