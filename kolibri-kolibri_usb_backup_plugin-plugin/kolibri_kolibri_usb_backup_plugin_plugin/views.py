from django.views.generic.base import TemplateView
# from .models import BackupSchedule
# import JsonResponse
# from .models import MyPluginData

# # def my_view(request):
#     # To save data
# new_entry = MyPluginData(name="Example Item", description="Plugin info")
# new_entry.save()

# # To retrieve data
# all_items = MyPluginData.objects.all()
# print(all_items)

class UsbBackupView(TemplateView):
    template_name = "usb_backup.html"

# def backup_schedule_api():
#     schedule = BackupSchedule.objects.first()  # or your query logic
#     console.log(schedule)
    # return JsonResponse({
    #     'frequency': schedule.frequency,
    #     'hour': str(schedule.hour),
    #     'day_of_week': schedule.day_of_week,
    # })