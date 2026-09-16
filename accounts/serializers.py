from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    accept_terms = serializers.BooleanField(write_only=True, required=False, default=True)
    accept_privacy = serializers.BooleanField(write_only=True, required=False, default=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "phone_number",
            "first_name",
            "last_name",
            "password",
            "accept_terms",
            "accept_privacy",
        )

    def create(self, validated_data):
        accept_terms = validated_data.pop("accept_terms", True)
        accept_privacy = validated_data.pop("accept_privacy", True)
        if (accept_terms is False) or (accept_privacy is False):
            raise serializers.ValidationError("Terms and privacy policy acceptance are required")
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        if "email" in attrs and "password" in attrs:
            attrs[self.username_field] = attrs.pop("email")
        return super().validate(attrs)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "phone_number", "first_name", "last_name")
        read_only_fields = ("id", "username")


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
