from django.http import JsonResponse
from django.views import View
import subprocess
from kolibri.core.device.permissions import IsSuperuser
from rest_framework.response import Response
from kolibri.core.tasks.registry import TaskRegistry
# from .usb import find_usb_microsd

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