from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from appointments.models import Appointment, AppointmentStatus
from specialists.models import Specialist, WorkingHour, Weekday


User = get_user_model()


def next_weekday(weekday: int) -> date:
	"""Return the nearest future date that falls on the given weekday (0=Monday)."""
	today = date.today()
	days_ahead = weekday - today.weekday()
	if days_ahead <= 0:
		days_ahead += 7
	return today + timedelta(days=days_ahead)


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
		self.target_date = next_weekday(Weekday.MONDAY)

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

	def test_past_date_booking_rejected(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(
			"/api/appointments/",
			{"specialist": self.specialist.id, "date": "2020-01-06", "time": "10:00:00"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_out_of_working_hours_rejected(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.post(
			"/api/appointments/",
			{"specialist": self.specialist.id, "date": self.target_date, "time": "08:00:00"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_cancel_by_owner(self):
		appointment = Appointment.objects.create(
			user=self.user, specialist=self.specialist,
			date=self.target_date, time="10:00:00",
		)
		self.client.force_authenticate(user=self.user)
		response = self.client.patch(f"/api/appointments/{appointment.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_cancel_by_non_owner_returns_403(self):
		appointment = Appointment.objects.create(
			user=self.user, specialist=self.specialist,
			date=self.target_date, time="10:00:00",
		)
		self.client.force_authenticate(user=self.other_user)
		response = self.client.patch(f"/api/appointments/{appointment.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	# ------------------------------------------------------------------ #
	# Slot-alignment validation                                            #
	# ------------------------------------------------------------------ #

	def test_aligned_time_accepted(self):
		"""10:30 aligns with 30-min grid starting at 09:00."""
		self.client.force_authenticate(user=self.user)
		response = self.client.post(
			"/api/appointments/",
			{"specialist": self.specialist.id, "date": self.target_date, "time": "10:30:00"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_unaligned_time_rejected(self):
		"""10:15 does not align with 30-min grid starting at 09:00."""
		self.client.force_authenticate(user=self.user)
		response = self.client.post(
			"/api/appointments/",
			{"specialist": self.specialist.id, "date": self.target_date, "time": "10:15:00"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_alignment_with_60min_slot_duration(self):
		self.specialist.slot_duration = 60
		self.specialist.save()
		self.client.force_authenticate(user=self.user)
		# 10:30 is NOT aligned to 60-min grid from 09:00 (09:00, 10:00, 11:00…)
		response = self.client.post(
			"/api/appointments/",
			{"specialist": self.specialist.id, "date": self.target_date, "time": "10:30:00"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AppointmentFieldTests(APITestCase):
	"""Tests for the notes, duration, and updated_at fields."""

	def setUp(self):
		self.user = User.objects.create_user("user1", password="strongpass123")
		self.admin = User.objects.create_superuser("admin", "admin@example.com", "adminpass123")
		self.specialist = Specialist.objects.create(name="Dr. Field", profession="General", slot_duration=30)
		WorkingHour.objects.create(
			specialist=self.specialist,
			day=Weekday.MONDAY,
			start_time=time(9, 0),
			end_time=time(17, 0),
		)
		self.target_date = next_weekday(Weekday.MONDAY)

	def _create_appointment(self, t="10:00:00", notes="", duration=None):
		payload = {"specialist": self.specialist.id, "date": self.target_date, "time": t}
		if notes:
			payload["notes"] = notes
		if duration is not None:
			payload["duration"] = duration
		self.client.force_authenticate(user=self.user)
		return self.client.post("/api/appointments/", payload, format="json")

	# ------------------------------------------------------------------ #
	# notes                                                                #
	# ------------------------------------------------------------------ #

	def test_notes_default_to_empty_string(self):
		response = self._create_appointment()
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["notes"], "")

	def test_notes_can_be_set_on_creation(self):
		response = self._create_appointment(notes="First visit")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["notes"], "First visit")

	def test_notes_persisted_to_db(self):
		self._create_appointment(notes="Follow-up")
		appt = Appointment.objects.get()
		self.assertEqual(appt.notes, "Follow-up")

	def test_notes_exposed_in_list_view(self):
		Appointment.objects.create(
			user=self.user, specialist=self.specialist,
			date=self.target_date, time=time(10, 0), notes="Important",
		)
		self.client.force_authenticate(user=self.user)
		response = self.client.get("/api/my-appointments/")
		self.assertEqual(response.data[0]["notes"], "Important")

	# ------------------------------------------------------------------ #
	# duration                                                             #
	# ------------------------------------------------------------------ #

	def test_duration_defaults_to_specialist_slot_duration(self):
		response = self._create_appointment()
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["duration"], self.specialist.slot_duration)

	def test_duration_can_be_overridden_on_creation(self):
		response = self._create_appointment(duration=60)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(response.data["duration"], 60)

	def test_duration_persisted_to_db(self):
		self._create_appointment(duration=45)
		appt = Appointment.objects.get()
		self.assertEqual(appt.duration, 45)

	def test_duration_is_exposed_in_api(self):
		self._create_appointment()
		self.client.force_authenticate(user=self.user)
		response = self.client.get("/api/my-appointments/")
		self.assertIn("duration", response.data[0])

	# ------------------------------------------------------------------ #
	# updated_at                                                           #
	# ------------------------------------------------------------------ #

	def test_updated_at_set_on_creation(self):
		response = self._create_appointment()
		self.assertIsNotNone(response.data["updated_at"])

	def test_updated_at_changes_when_status_changes(self):
		appt = Appointment.objects.create(
			user=self.user, specialist=self.specialist,
			date=self.target_date, time=time(10, 0),
		)
		original_updated_at = appt.updated_at
		self.client.force_authenticate(user=self.admin)
		self.client.patch(f"/api/appointments/{appt.id}/confirm/")
		appt.refresh_from_db()
		self.assertGreaterEqual(appt.updated_at, original_updated_at)

	def test_updated_at_is_read_only_in_api(self):
		"""Clients cannot manually set updated_at."""
		payload = {
			"specialist": self.specialist.id,
			"date": self.target_date,
			"time": "10:00:00",
			"updated_at": "2000-01-01T00:00:00Z",
		}
		self.client.force_authenticate(user=self.user)
		response = self.client.post("/api/appointments/", payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		# The returned updated_at must NOT be the supplied value
		self.assertNotEqual(response.data["updated_at"], "2000-01-01T00:00:00Z")


class AppointmentLifecycleTests(APITestCase):
	"""Tests for valid and invalid status transitions."""

	def setUp(self):
		self.user = User.objects.create_user("user1", password="strongpass123")
		self.admin = User.objects.create_superuser("admin", "admin@example.com", "adminpass123")
		self.specialist = Specialist.objects.create(name="Dr. Lifecycle", profession="General")
		WorkingHour.objects.create(
			specialist=self.specialist,
			day=Weekday.MONDAY,
			start_time=time(9, 0),
			end_time=time(17, 0),
		)
		self.monday = next_weekday(Weekday.MONDAY)

	def _make_appointment(self, appt_status=AppointmentStatus.PENDING, t="10:00:00"):
		return Appointment.objects.create(
			user=self.user, specialist=self.specialist,
			date=self.monday, time=t, status=appt_status,
		)

	# ------------------------------------------------------------------ #
	# VALID transitions                                                    #
	# ------------------------------------------------------------------ #

	def test_pending_to_confirmed(self):
		appt = self._make_appointment(AppointmentStatus.PENDING)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/confirm/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		appt.refresh_from_db()
		self.assertEqual(appt.status, AppointmentStatus.CONFIRMED)

	def test_pending_to_cancelled(self):
		appt = self._make_appointment(AppointmentStatus.PENDING)
		self.client.force_authenticate(user=self.user)
		response = self.client.patch(f"/api/appointments/{appt.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		appt.refresh_from_db()
		self.assertEqual(appt.status, AppointmentStatus.CANCELLED)

	def test_confirmed_to_completed(self):
		appt = self._make_appointment(AppointmentStatus.CONFIRMED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		appt.refresh_from_db()
		self.assertEqual(appt.status, AppointmentStatus.COMPLETED)

	def test_confirmed_to_no_show(self):
		appt = self._make_appointment(AppointmentStatus.CONFIRMED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/no-show/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		appt.refresh_from_db()
		self.assertEqual(appt.status, AppointmentStatus.NO_SHOW)

	def test_confirmed_to_cancelled(self):
		appt = self._make_appointment(AppointmentStatus.CONFIRMED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		appt.refresh_from_db()
		self.assertEqual(appt.status, AppointmentStatus.CANCELLED)

	# ------------------------------------------------------------------ #
	# INVALID transitions — PENDING source                                #
	# ------------------------------------------------------------------ #

	def test_pending_to_completed_rejected(self):
		appt = self._make_appointment(AppointmentStatus.PENDING)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		appt.refresh_from_db()
		self.assertEqual(appt.status, AppointmentStatus.PENDING)

	def test_pending_to_no_show_rejected(self):
		appt = self._make_appointment(AppointmentStatus.PENDING)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/no-show/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		appt.refresh_from_db()
		self.assertEqual(appt.status, AppointmentStatus.PENDING)

	# ------------------------------------------------------------------ #
	# INVALID transitions — COMPLETED source (terminal)                   #
	# ------------------------------------------------------------------ #

	def test_completed_to_confirmed_rejected(self):
		appt = self._make_appointment(AppointmentStatus.COMPLETED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/confirm/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_completed_to_cancelled_rejected(self):
		appt = self._make_appointment(AppointmentStatus.COMPLETED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_completed_to_no_show_rejected(self):
		appt = self._make_appointment(AppointmentStatus.COMPLETED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/no-show/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_completed_to_completed_rejected(self):
		appt = self._make_appointment(AppointmentStatus.COMPLETED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	# ------------------------------------------------------------------ #
	# INVALID transitions — NO_SHOW source (terminal)                     #
	# ------------------------------------------------------------------ #

	def test_no_show_to_confirmed_rejected(self):
		appt = self._make_appointment(AppointmentStatus.NO_SHOW)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/confirm/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_no_show_to_completed_rejected(self):
		appt = self._make_appointment(AppointmentStatus.NO_SHOW)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_no_show_to_cancelled_rejected(self):
		appt = self._make_appointment(AppointmentStatus.NO_SHOW)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_no_show_to_no_show_rejected(self):
		appt = self._make_appointment(AppointmentStatus.NO_SHOW)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/no-show/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	# ------------------------------------------------------------------ #
	# INVALID transitions — CANCELLED source (terminal)                   #
	# ------------------------------------------------------------------ #

	def test_cancelled_to_confirmed_rejected(self):
		appt = self._make_appointment(AppointmentStatus.CANCELLED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/confirm/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_cancelled_to_completed_rejected(self):
		appt = self._make_appointment(AppointmentStatus.CANCELLED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_cancelled_to_no_show_rejected(self):
		appt = self._make_appointment(AppointmentStatus.CANCELLED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/no-show/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_cancelled_to_cancelled_rejected(self):
		appt = self._make_appointment(AppointmentStatus.CANCELLED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/cancel/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	# ------------------------------------------------------------------ #
	# DB state & response payload                                          #
	# ------------------------------------------------------------------ #

	def test_complete_response_payload(self):
		appt = self._make_appointment(AppointmentStatus.CONFIRMED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertIn("detail", response.data)

	def test_no_show_response_payload(self):
		appt = self._make_appointment(AppointmentStatus.CONFIRMED)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/no-show/")
		self.assertIn("detail", response.data)

	def test_invalid_transition_error_message_contains_statuses(self):
		appt = self._make_appointment(AppointmentStatus.PENDING)
		self.client.force_authenticate(user=self.admin)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		# Error must mention both statuses so the client knows what happened
		error_text = str(response.data)
		self.assertIn("pending", error_text)
		self.assertIn("completed", error_text)

	def test_complete_requires_admin(self):
		appt = self._make_appointment(AppointmentStatus.CONFIRMED)
		self.client.force_authenticate(user=self.user)
		response = self.client.patch(f"/api/appointments/{appt.id}/complete/")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_no_show_requires_admin(self):
		appt = self._make_appointment(AppointmentStatus.CONFIRMED)
		self.client.force_authenticate(user=self.user)
		response = self.client.patch(f"/api/appointments/{appt.id}/no-show/")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	# ------------------------------------------------------------------ #
	# Slot availability regression                                         #
	# ------------------------------------------------------------------ #

	def test_cancelled_appointment_releases_slot(self):
		"""After cancellation the slot must appear in available-slots again."""
		appt = self._make_appointment(AppointmentStatus.PENDING, t="09:00:00")
		self.client.force_authenticate(user=self.user)
		self.client.patch(f"/api/appointments/{appt.id}/cancel/")
		response = self.client.get(
			f"/api/specialists/{self.specialist.id}/available-slots/",
			{"date": self.monday},
		)
		self.assertIn("09:00", response.data["slots"])

	def test_confirmed_appointment_blocks_slot(self):
		"""A confirmed appointment must not appear in available-slots."""
		self._make_appointment(AppointmentStatus.CONFIRMED, t="09:00:00")
		response = self.client.get(
			f"/api/specialists/{self.specialist.id}/available-slots/",
			{"date": self.monday},
		)
		self.assertNotIn("09:00", response.data["slots"])

	def test_completed_appointment_releases_slot(self):
		"""A completed appointment is no longer PENDING/CONFIRMED, so slot is free."""
		self._make_appointment(AppointmentStatus.COMPLETED, t="09:00:00")
		response = self.client.get(
			f"/api/specialists/{self.specialist.id}/available-slots/",
			{"date": self.monday},
		)
		self.assertIn("09:00", response.data["slots"])

	def test_no_show_appointment_releases_slot(self):
		self._make_appointment(AppointmentStatus.NO_SHOW, t="09:00:00")
		response = self.client.get(
			f"/api/specialists/{self.specialist.id}/available-slots/",
			{"date": self.monday},
		)
		self.assertIn("09:00", response.data["slots"])

