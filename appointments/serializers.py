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

        weekday = date.weekday()
        in_hours = WorkingHour.objects.filter(
            specialist=specialist,
            day=weekday,
            start_time__lte=time,
            end_time__gt=time,
        ).exists()
        if not in_hours:
            raise serializers.ValidationError("Selected time is outside specialist working hours.")

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
