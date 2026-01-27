from django.urls import re_path
from .views import UsbBackupView

urlpatterns = [
    re_path(r"^$", UsbBackupView.as_view(), name="usb_backup")
]