from django.http import JsonResponse
from django.views import View
import json
import subprocess
from kolibri.core.device.permissions import IsSuperuser
from kolibri.core.tasks.registry import TaskRegistry
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import BackupSchedule



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

class DetectUSBView(APIView):
    """
    Returns a list of USB drives and SD cards detected on this Raspberry Pi.
    Uses lsblk to find removable block devices (USB sticks, SD cards via USB reader).
    """
    permission_classes = (IsSuperuser,)

    def get(self, request):
        try:
            result = subprocess.run(
                [
                    "lsblk",
                    "-J",        # JSON output
                    "-o", "NAME,SIZE,TRAN,RM,MOUNTPOINT,LABEL,MODEL",
                    "-d",        # top-level devices only (no partitions)
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                return Response(
                    {"error": "lsblk failed: " + result.stderr.strip()},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            data = json.loads(result.stdout)
            devices = []
            for dev in data.get("blockdevices", []):
                # Include devices connected via USB, or flagged as removable (rm=True/"1")
                is_usb = dev.get("tran") == "usb"
                is_removable = dev.get("rm") in (True, "1", 1)
                if is_usb or is_removable:
                    name = dev.get("name", "")
                    label = dev.get("label") or dev.get("model") or name
                    size = dev.get("size", "")
                    devices.append({
                        "path": "/dev/{}".format(name),
                        "name": name,
                        "label": "{} ({})".format(label, size) if size else label,
                        "size": size,
                        "mountpoint": dev.get("mountpoint"),
                    })

            return Response({"devices": devices})

        except FileNotFoundError:
            return Response(
                {"error": "lsblk not found on this system"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except subprocess.TimeoutExpired:
            return Response(
                {"error": "Device detection timed out"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )