from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import (
	CustomTokenObtainPairSerializer,
	LogoutSerializer,
	RegisterSerializer,
	UserProfileSerializer,
)


class RegisterView(generics.CreateAPIView):
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
	serializer_class = CustomTokenObtainPairSerializer
	permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, *args, **kwargs):
		serializer = LogoutSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		refresh_token = serializer.validated_data["refresh"]
		token = RefreshToken(refresh_token)
		token.blacklist()
		return Response({"detail": "Logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)


class ProfileView(generics.RetrieveAPIView):
	serializer_class = UserProfileSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		return self.request.user
