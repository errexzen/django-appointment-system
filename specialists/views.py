from rest_framework import generics, permissions

from specialists.models import Specialist, WorkingHour
from specialists.serializers import SpecialistSerializer, WorkingHourSerializer


class SpecialistListView(generics.ListCreateAPIView):
	queryset = Specialist.objects.all()
	serializer_class = SpecialistSerializer
	search_fields = ["profession"]

	def get_permissions(self):
		if self.request.method == "POST":
			return [permissions.IsAdminUser()]
		return [permissions.AllowAny()]


class SpecialistDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Specialist.objects.all()
	serializer_class = SpecialistSerializer

	def get_permissions(self):
		if self.request.method in ["PUT", "PATCH", "DELETE"]:
			return [permissions.IsAdminUser()]
		return [permissions.AllowAny()]


class SpecialistWorkingHoursView(generics.ListAPIView):
	serializer_class = WorkingHourSerializer
	permission_classes = [permissions.AllowAny]

	def get_queryset(self):
		return WorkingHour.objects.filter(specialist_id=self.kwargs["pk"])
