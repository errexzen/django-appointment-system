from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment, AppointmentStatus
from appointments.permissions import IsOwnerOrAdmin
from appointments.serializers import AppointmentSerializer, AppointmentStatusSerializer


class AppointmentCreateView(generics.CreateAPIView):
	serializer_class = AppointmentSerializer
	permission_classes = [permissions.IsAuthenticated]


class MyAppointmentListView(generics.ListAPIView):
	serializer_class = AppointmentSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return Appointment.objects.filter(user=self.request.user)


class AppointmentCancelView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		self.check_object_permissions(request, appointment)
		serializer = AppointmentStatusSerializer(
			appointment,
			data={"status": AppointmentStatus.CANCELLED},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Appointment cancelled successfully."}, status=status.HTTP_200_OK)


class AppointmentConfirmView(APIView):
	permission_classes = [permissions.IsAdminUser]

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		serializer = AppointmentStatusSerializer(
			appointment,
			data={"status": AppointmentStatus.CONFIRMED},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Appointment confirmed successfully."}, status=status.HTTP_200_OK)


class AppointmentCompleteView(APIView):
	permission_classes = [permissions.IsAdminUser]

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		serializer = AppointmentStatusSerializer(
			appointment,
			data={"status": AppointmentStatus.COMPLETED},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Appointment marked as completed."}, status=status.HTTP_200_OK)


class AppointmentNoShowView(APIView):
	permission_classes = [permissions.IsAdminUser]

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		serializer = AppointmentStatusSerializer(
			appointment,
			data={"status": AppointmentStatus.NO_SHOW},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Appointment marked as no-show."}, status=status.HTTP_200_OK)
