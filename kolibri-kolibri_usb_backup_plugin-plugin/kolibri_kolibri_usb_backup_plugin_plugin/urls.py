from django.urls import re_path
from .views import UsbBackupView
from .api import RunBackupView, BackupScheduleView
# from .views import backup_schedule_api
# ADD DetectUSBView here


urlpatterns = [
    re_path(r"^$", UsbBackupView.as_view(), name="usb_backup"),
    re_path(r"^run_backup/", RunBackupView.as_view(), name="run_backup"),
    re_path(r"^api/backup_schedule/$", BackupScheduleView.as_view(), name="backup_schedule"),
    # re_path(r'^api/backup-schedule/', backup_schedule_api, name='backup-schedule'),
    # re_path(r"^api/detect-usb/", DetectUSBView.as_view(), name="detect-usb"),  # ← new
]
