from rest_framework import serializers

from specialists.models import Specialist, WorkingHour


class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ("id", "name", "profession", "description", "image", "created_at")
        read_only_fields = ("id", "created_at")


class WorkingHourSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source="get_day_display", read_only=True)

    class Meta:
        model = WorkingHour
        fields = ("id", "specialist", "day", "day_display", "start_time", "end_time")
        read_only_fields = ("id",)
