from django.db import models

class MyPluginData(models.Model):
    user_id = models.CharField(max_length=100)
    data_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# class BackupSchedule(models.Model):
#     # Number of hours between backups
#     frequency = models.IntegerField(
#         help_text="Hours before the next backup runs."
#     )

#     # Time of day to run (used when frequency > 24 hours)
#     hour = models.TimeField(
#         null=True,
#         blank=True,
#         help_text="Time to run backup if frequency is greater than 24 hours."
#     )

#     # Day of week to run (used when frequency > 168 hours / weekly)
#     day_of_week = models.IntegerField(
#         null=True,
#         blank=True,
#         help_text="Day of week to run backup (0-6) if frequency is greater than 168 hours."
#     )

# class BackupStatus(models.Model):
#     last_successful_backup = models.DateTimeField(
#         null=True,
#         blank=True,
#         help_text="Timestamp of the most recent successful backup."
#     )