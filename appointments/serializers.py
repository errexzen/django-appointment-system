from django.utils import timezone
from rest_framework import serializers

from appointments.models import Appointment, AppointmentStatus
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
            "created_at",
        )
        read_only_fields = ("id", "user", "status", "created_at")

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
        return super().create(validated_data)


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ("status",)
