from django.http import JsonResponse
from django.views import View
import subprocess
from kolibri.core.device.permissions import IsSuperuser
from kolibri.core.tasks.registry import TaskRegistry
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import BackupSchedule
# from .usb import find_usb_microsd



class BackupScheduleView(APIView):
    permission_classes = (IsSuperuser,)

    def get(self, request):
        schedule = BackupSchedule.objects.first()
        if not schedule:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({
            "frequency": schedule.frequency,
            "hour": schedule.hour.strftime("%H:%M:%S") if schedule.hour else None,
            "day_of_week": schedule.day_of_week,
        })

    def post(self, request):
        from datetime import time
        data = request.data
        
        # Parse hour string "HH:MM" to time object if provided
        hour_time = None
        if data.get("hour"):
            try:
                h, m = data.get("hour").split(':')
                hour_time = time(int(h), int(m))
            except (ValueError, AttributeError, TypeError):
                hour_time = None
        
        # Use defaults to ensure required fields are set on creation
        schedule, _ = BackupSchedule.objects.get_or_create(
            pk=1,
            defaults={
                "frequency": data.get("frequency", 3600),  # fallback: 1 hour
                "hour": hour_time,
                "day_of_week": data.get("day_of_week"),
            }
        )
        # Update the existing record with new values
        schedule.frequency = data.get("frequency")
        schedule.hour = hour_time
        schedule.day_of_week = data.get("day_of_week")
        schedule.save()
        return Response({"status": "ok"}, status=status.HTTP_200_OK)



# class RunBackupView(View):
#     def post(self, request, *args, **kwargs):
#         # this output will appear on the Kolibri server console/log
#         print("hello world")
#         return JsonResponse({"job_id": "hello-world-job"})


class RunBackupView(View):
    """
    Trigger a one-off immediate backup run for a facility.
    """

    permission_classes = (IsSuperuser,)

    def post(self, request):
        # facility_id = request.data.get("facility")
        # if not facility_id:
        #     return Response({"detail": "Missing 'facility' field"}, status=400)

        try:
            task = TaskRegistry["kolibri.core.auth.tasks.dataportalsync"]
        except KeyError:
            return Response({"detail": "Backup task not available"}, status=500)

        # Enqueue immediate job for this facility. Provide facility_id to the Job
        # and pass the function kwargs under `kwargs`.
        job_id = task.enqueue(
            args=["sync"], 
        #    kwargs={"facility": facility_id}, 
        )
        print('backing up!!!!!!!!!!!!!!!!')
        subprocess.run(["touch", "/tmp/test_kolibri"], check=True)
        subprocess.run(
            ["sudo", "systemctl", "start", "kolibri-rpi-clone.service"],
            check=True
        )
        return Response({"job_id": job_id}, status=202)

# class DetectUSBView(View):
#     """
#     Returns a list of USB-connected MicroSD cards detected on this Pi.
#     """
#     def get(self, request):
#         try:
#             devices = find_usb_microsd()
#         except RuntimeError as e:
#             return JsonResponse({"error": str(e)}, status=500)
#         return JsonResponse({"devices": devices})