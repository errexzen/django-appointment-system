from rest_framework import serializers

from organizations.selectors import get_request_organization
from staff.models import StaffProfile


class StaffProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = StaffProfile
        fields = (
            "id",
            "user",
            "user_email",
            "organization",
            "job_title",
            "bio",
            "profile_image",
            "phone_number",
            "is_active",
            "is_accepting_bookings",
            "appointment_color",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "organization", "created_at", "updated_at")

    def create(self, validated_data):
        validated_data["organization"] = get_request_organization(self.context["request"])
        return super().create(validated_data)
