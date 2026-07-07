from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from specialists.models import Specialist


User = get_user_model()


class SpecialistAPITests(APITestCase):
	def setUp(self):
		self.specialist = Specialist.objects.create(
			name="Dr. Smith",
			profession="Cardiologist",
			description="Heart specialist",
		)
		self.admin = User.objects.create_superuser("admin", "admin@example.com", "adminpass123")

	def test_list_specialists(self):
		response = self.client.get("/api/specialists/")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)

	def test_search_specialists_by_profession(self):
		response = self.client.get("/api/specialists/?search=Cardio")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)

	def test_non_admin_cannot_create_specialist(self):
		user = User.objects.create_user("normal", password="strongpass123")
		self.client.force_authenticate(user=user)
		response = self.client.post(
			"/api/specialists/",
			{"name": "Dr. X", "profession": "Dentist", "description": "desc"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_create_specialist(self):
		self.client.force_authenticate(user=self.admin)
		response = self.client.post(
			"/api/specialists/",
			{"name": "Dr. Jane", "profession": "Dentist", "description": "desc"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
