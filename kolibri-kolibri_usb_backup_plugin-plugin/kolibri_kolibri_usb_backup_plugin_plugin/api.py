from datetime import datetime, timedelta, time
import subprocess
from django.utils import timezone
from django.views import View
from kolibri.core.device.permissions import IsSuperuser
from kolibri.core.tasks.registry import TaskRegistry
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import BackupSchedule


def _to_iso(dt):
    if not dt:
        return None
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, timezone.get_current_timezone())
    return dt.isoformat()


def compute_next_backup(frequency, hour=None, day_of_week=None, from_dt=None):
    now = from_dt or timezone.now()
    if not frequency:
        return None

    # frequency is interpreted in seconds
    try:
        interval = int(frequency)
    except (TypeError, ValueError):
        return None

    # If day and hour are provided, compute next weekly occurrence.
    if day_of_week is not None and hour is not None:
        # day_of_week expected 0=Sunday ... 6=Saturday
        target_datetime = now.astimezone(timezone.get_current_timezone()).replace(
            hour=hour.hour,
            minute=hour.minute,
            second=0,
            microsecond=0,
        )
        weekday_today = target_datetime.weekday()  # Monday=0 .. Sunday=6
        # Convert to same numbering if needed: plugin uses 0=Sunday
        target_day = (day_of_week + 6) % 7
        days_until = (target_day - weekday_today) % 7
        if days_until == 0 and target_datetime <= now:
            days_until = 7
        target_datetime = target_datetime + timedelta(days=days_until)
        return target_datetime

    # If only hour is provided, schedule next daily occurrence at that hour.
    if hour is not None:
        target_datetime = now.astimezone(timezone.get_current_timezone()).replace(
            hour=hour.hour,
            minute=hour.minute,
            second=0,
            microsecond=0,
        )
        if target_datetime <= now:
            target_datetime += timedelta(days=1)
        return target_datetime

    # Fallback: frequency interval from now.
    return now + timedelta(seconds=interval)


class BackupScheduleView(APIView):
    permission_classes = (IsSuperuser,)

    def get(self, request):
        schedule = BackupSchedule.objects.first()
        if not schedule:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({
            "frequency": schedule.frequency,
            "hour": schedule.hour.strftime("%H:%M") if schedule.hour else None,
            "day_of_week": schedule.day_of_week,
            "last_backup": _to_iso(schedule.last_backup),
            "next_backup": _to_iso(schedule.next_backup),
        })

    def post(self, request):
        data = request.data

        # Parse hour string "HH:MM" to time object if provided
        hour_time = None
        if data.get("hour"):
            try:
                h, m = data.get("hour").split(':')
                hour_time = time(int(h), int(m))
            except (ValueError, AttributeError, TypeError):
                hour_time = None

        frequency = data.get("frequency")
        day_of_week = data.get("day_of_week")

        # Create or update schedule
        schedule, _ = BackupSchedule.objects.get_or_create(pk=1, defaults={
            "frequency": frequency or 3600,
            "hour": hour_time,
            "day_of_week": day_of_week,
        })
        schedule.frequency = frequency or schedule.frequency
        schedule.hour = hour_time
        schedule.day_of_week = day_of_week
        schedule.next_backup = compute_next_backup(
            schedule.frequency,
            hour=schedule.hour,
            day_of_week=schedule.day_of_week,
        )
        schedule.save()

        return Response({
            "frequency": schedule.frequency,
            "hour": schedule.hour.strftime("%H:%M") if schedule.hour else None,
            "day_of_week": schedule.day_of_week,
            "last_backup": _to_iso(schedule.last_backup),
            "next_backup": _to_iso(schedule.next_backup),
        })

    def delete(self, request):
        schedule = BackupSchedule.objects.first()
        if not schedule:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        schedule.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)


class RunBackupView(View):
    """
    Trigger a one-off immediate backup run for a facility.
    """

    permission_classes = (IsSuperuser,)

    def post(self, request):
        try:
            task = TaskRegistry["kolibri.core.auth.tasks.dataportalsync"]
        except KeyError:
            return Response({"detail": "Backup task not available"}, status=500)

        try:
            job_id = task.enqueue(args=["sync"])
            subprocess.run(["touch", "/tmp/test_kolibri"], check=True)
            subprocess.run(
                ["sudo", "systemctl", "start", "kolibri-rpi-clone.service"],
                check=True,
            )
        except Exception as exc:
            return Response({"detail": str(exc)}, status=500)

        schedule = BackupSchedule.objects.first()
        if schedule:
            schedule.last_backup = timezone.now()
            schedule.next_backup = compute_next_backup(
                schedule.frequency,
                hour=schedule.hour,
                day_of_week=schedule.day_of_week,
                from_dt=schedule.last_backup,
            )
            schedule.save()

        return Response({"job_id": job_id}, status=202)
