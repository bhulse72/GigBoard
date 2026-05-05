from django.db import migrations


def reset_sequence(apps, schema_editor):
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT setval('notifications_notification_id_seq', "
            "(SELECT COALESCE(MAX(id), 1) FROM notifications_notification))"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_copy_data'),
    ]

    operations = [
        migrations.RunPython(reset_sequence, migrations.RunPython.noop),
    ]
