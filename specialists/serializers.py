from rest_framework import serializers

from specialists.models import Specialist, WorkingHour


class SpecialistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialist
        fields = ("id", "name", "profession", "description", "image", "slot_duration", "created_at")
        read_only_fields = ("id", "created_at")


class WorkingHourSerializer(serializers.ModelSerializer):
    day_display = serializers.CharField(source="get_day_display", read_only=True)

    class Meta:
        model = WorkingHour
        fields = ("id", "specialist", "day", "day_display", "start_time", "end_time")
        read_only_fields = ("id",)


class WorkingHourWriteSerializer(serializers.ModelSerializer):
    """Used for POST (create). specialist is injected from URL, not the request body."""

    class Meta:
        model = WorkingHour
        fields = ("id", "day", "start_time", "end_time")
        read_only_fields = ("id",)

    def to_representation(self, instance):
        return WorkingHourSerializer(instance, context=self.context).data

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        day = attrs.get("day")

        if start_time >= end_time:
            raise serializers.ValidationError("Start time must be before end time.")

        specialist = self.context["specialist"]
        overlapping = WorkingHour.objects.filter(
            specialist=specialist,
            day=day,
            start_time__lt=end_time,
            end_time__gt=start_time,
        )
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)
        if overlapping.exists():
            raise serializers.ValidationError(
                "This working hour range overlaps with an existing range for this day."
            )

        return attrs
