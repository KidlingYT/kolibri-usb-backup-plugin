from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kolibri_kolibri_usb_backup_plugin_plugin', '0002_backupschedule_backupstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='backupschedule',
            name='last_backup',
            field=models.DateTimeField(blank=True, help_text='Timestamp of the most recent successful backup.', null=True),
        ),
        migrations.AddField(
            model_name='backupschedule',
            name='next_backup',
            field=models.DateTimeField(blank=True, help_text='Timestamp of the next scheduled backup.', null=True),
        ),
    ]
