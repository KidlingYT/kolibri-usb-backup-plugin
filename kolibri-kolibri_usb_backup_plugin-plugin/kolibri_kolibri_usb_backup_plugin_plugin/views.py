from django.views.generic.base import TemplateView

class UsbBackupView(TemplateView):
    template_name = "usb_backup.html"