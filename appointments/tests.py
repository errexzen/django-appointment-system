from datetime import date, time

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from appointments.models import Appointment, AppointmentStatus
from specialists.models import Specialist, WorkingHour, Weekday


User = get_user_model()


class AppointmentAPITests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user("user1", password="strongpass123")
		self.other_user = User.objects.create_user("user2", password="strongpass123")
		self.admin = User.objects.create_superuser("admin", "admin@example.com", "adminpass123")
		self.specialist = Specialist.objects.create(name="Dr. House", profession="General")
		WorkingHour.objects.create(
			specialist=self.specialist,
			day=Weekday.MONDAY,
			start_time=time(9, 0),
			end_time=time(17, 0),
		)
		self.target_date = date(2026, 7, 13)  # Monday

	def test_appointment_creation(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(
			"/api/appointments/",
			{
				"specialist": self.specialist.id,
				"date": self.target_date,
				"time": "10:00:00",
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(Appointment.objects.count(), 1)

	def test_duplicate_appointment_prevention(self):
		Appointment.objects.create(
			user=self.user,
			specialist=self.specialist,
			date=self.target_date,
			time="10:00:00",
			status=AppointmentStatus.PENDING,
		)
		self.client.force_authenticate(user=self.other_user)
		response = self.client.post(
			"/api/appointments/",
			{
				"specialist": self.specialist.id,
				"date": self.target_date,
				"time": "10:00:00",
			},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_user_cannot_confirm_appointment(self):
		appointment = Appointment.objects.create(
			user=self.user,
			specialist=self.specialist,
			date=self.target_date,
			time="11:00:00",
		)
		self.client.force_authenticate(user=self.user)
		response = self.client.patch(f"/api/appointments/{appointment.id}/confirm/", format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_confirm_appointment(self):
		appointment = Appointment.objects.create(
			user=self.user,
			specialist=self.specialist,
			date=self.target_date,
			time="12:00:00",
		)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appointment.id}/confirm/", format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		appointment.refresh_from_db()
		self.assertEqual(appointment.status, AppointmentStatus.CONFIRMED)
