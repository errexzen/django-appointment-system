from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment, AppointmentStatus
from appointments.permissions import (
	IsAdminOrAssignedSpecialist,
	IsAppointmentCanceller,
	IsNotSpecialist,
	IsOwnerOrAdmin,
)
from appointments.serializers import AppointmentSerializer, AppointmentStatusSerializer


class AppointmentListCreateView(generics.ListCreateAPIView):
	"""GET: admin-only list of all appointments. POST: authenticated users create appointments."""

	serializer_class = AppointmentSerializer

	def get_permissions(self):
		if self.request.method == "GET":
			return [permissions.IsAdminUser()]
		# POST: authenticated non-specialists only
		return [permissions.IsAuthenticated(), IsNotSpecialist()]

	def get_queryset(self):
		return Appointment.objects.select_related("user", "specialist").all()


class MyAppointmentListView(generics.ListAPIView):
	serializer_class = AppointmentSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		return Appointment.objects.filter(user=self.request.user)


class AppointmentCancelView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAppointmentCanceller]

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
	permission_classes = [IsAdminOrAssignedSpecialist]

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		self.check_object_permissions(request, appointment)
		serializer = AppointmentStatusSerializer(
			appointment,
			data={"status": AppointmentStatus.CONFIRMED},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Appointment confirmed successfully."}, status=status.HTTP_200_OK)


class AppointmentCompleteView(APIView):
	permission_classes = [IsAdminOrAssignedSpecialist]

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		self.check_object_permissions(request, appointment)
		serializer = AppointmentStatusSerializer(
			appointment,
			data={"status": AppointmentStatus.COMPLETED},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Appointment marked as completed."}, status=status.HTTP_200_OK)


class AppointmentNoShowView(APIView):
	permission_classes = [IsAdminOrAssignedSpecialist]

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		self.check_object_permissions(request, appointment)
		serializer = AppointmentStatusSerializer(
			appointment,
			data={"status": AppointmentStatus.NO_SHOW},
			partial=True,
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Appointment marked as no-show."}, status=status.HTTP_200_OK)

		serializer.save()
		return Response({"detail": "Appointment marked as no-show."}, status=status.HTTP_200_OK)
