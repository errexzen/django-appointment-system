from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from appointments.models import Appointment, AppointmentStatus
from appointments.permissions import (
	IsAdminOrAssignedSpecialist,
	IsAppointmentCanceller,
	IsNotSpecialist,
	IsOwnerOrAdmin,
)
from appointments.serializers import (
	AppointmentRescheduleSerializer,
	AppointmentSerializer,
	AppointmentStatusSerializer,
)


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


class AppointmentRescheduleView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAppointmentCanceller]

	_RESCHEDULABLE = {AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED}

	def patch(self, request, pk, *args, **kwargs):
		appointment = get_object_or_404(Appointment, pk=pk)
		self.check_object_permissions(request, appointment)

		if appointment.status not in self._RESCHEDULABLE:
			return Response(
				{"detail": f"Cannot reschedule a '{appointment.status}' appointment."},
				status=status.HTTP_400_BAD_REQUEST,
			)

		serializer = AppointmentRescheduleSerializer(
			data=request.data,
			context={"appointment": appointment, "request": request},
		)
		serializer.is_valid(raise_exception=True)

		with transaction.atomic():
			appointment.date = serializer.validated_data["date"]
			appointment.time = serializer.validated_data["time"]
			appointment.save()

		return Response(
			AppointmentSerializer(appointment, context={"request": request}).data,
			status=status.HTTP_200_OK,
		)
