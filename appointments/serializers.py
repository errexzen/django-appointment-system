from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import serializers

from appointments.models import ALLOWED_TRANSITIONS, Appointment, AppointmentStatus
from specialists.models import WorkingHour


class AppointmentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    specialist_name = serializers.CharField(source="specialist.name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "user",
            "specialist",
            "specialist_name",
            "date",
            "time",
            "status",
            "notes",
            "duration",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "status", "created_at", "updated_at")

    def validate(self, attrs):
        specialist = attrs.get("specialist")
        date = attrs.get("date")
        time = attrs.get("time")

        if date < timezone.localdate():
            raise serializers.ValidationError("Cannot book an appointment in the past.")

        if date == timezone.localdate() and time <= timezone.localtime().time():
            raise serializers.ValidationError("Cannot book an appointment at a past time today.")

        weekday = date.weekday()
        working_hours = WorkingHour.objects.filter(
            specialist=specialist,
            day=weekday,
            start_time__lte=time,
            end_time__gt=time,
        )
        if not working_hours.exists():
            raise serializers.ValidationError("Selected time is outside specialist working hours.")

        slot_duration = specialist.slot_duration
        def _minutes(t):
            return t.hour * 60 + t.minute

        aligned = any(
            (_minutes(time) - _minutes(wh.start_time)) % slot_duration == 0
            for wh in working_hours
        )
        if not aligned:
            raise serializers.ValidationError(
                f"Selected time does not align with the {slot_duration}-minute slot grid."
            )

        duplicate_exists = Appointment.objects.filter(
            specialist=specialist,
            date=date,
            time=time,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED],
        ).exists()
        if duplicate_exists:
            raise serializers.ValidationError("This slot is already booked.")

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        if "duration" not in validated_data:
            validated_data["duration"] = validated_data["specialist"].slot_duration
        return super().create(validated_data)


class AppointmentStatusSerializer(serializers.ModelSerializer):
    """Used exclusively for status transitions. Validates lifecycle rules."""

    class Meta:
        model = Appointment
        fields = ("status",)

    def validate_status(self, new_status):
        current = self.instance.status
        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if new_status not in allowed:
            raise serializers.ValidationError(
                f"Cannot transition appointment from '{current}' to '{new_status}'."
            )
        return new_status


class AppointmentRescheduleSerializer(serializers.Serializer):
    """Validates the new date/time for a reschedule request."""

    date = serializers.DateField()
    time = serializers.TimeField()

    def validate(self, attrs):
        appointment = self.context["appointment"]
        new_date = attrs["date"]
        new_time = attrs["time"]
        specialist = appointment.specialist

        if appointment.date == new_date and appointment.time == new_time:
            raise serializers.ValidationError("New slot is identical to the current slot.")

        if new_date < timezone.localdate():
            raise serializers.ValidationError("Cannot reschedule to a past date.")

        if new_date == timezone.localdate() and new_time <= timezone.localtime().time():
            raise serializers.ValidationError("Cannot reschedule to a past time today.")

        weekday = new_date.weekday()
        working_hours = WorkingHour.objects.filter(
            specialist=specialist,
            day=weekday,
        )
        new_start = datetime.combine(new_date, new_time)
        new_end = new_start + timedelta(minutes=appointment.duration)
        fits_working_hours = any(
            wh.start_time <= new_time and new_end.time() <= wh.end_time
            and new_end.date() == new_date
            for wh in working_hours
        )
        if not fits_working_hours:
            raise serializers.ValidationError("Selected time is outside specialist working hours.")

        def _minutes(t):
            return t.hour * 60 + t.minute

        slot_duration = specialist.slot_duration
        aligned = any(
            wh.start_time <= new_time
            and (_minutes(new_time) - _minutes(wh.start_time)) % slot_duration == 0
            for wh in working_hours
        )
        if not aligned:
            raise serializers.ValidationError(
                f"Selected time does not align with the {slot_duration}-minute slot grid."
            )

        active_appointments = Appointment.objects.filter(
            specialist=specialist,
            date=new_date,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED],
        ).exclude(pk=appointment.pk)
        for other in active_appointments:
            other_start = datetime.combine(other.date, other.time)
            other_end = other_start + timedelta(minutes=other.duration)
            if new_start < other_end and other_start < new_end:
                raise serializers.ValidationError("This slot overlaps an existing appointment.")

        return attrs
