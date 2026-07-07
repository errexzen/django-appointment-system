from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthAPITests(APITestCase):
	def test_user_registration(self):
		payload = {
			"username": "testuser",
			"email": "test@example.com",
			"phone_number": "09120000000",
			"password": "strongpass123",
		}
		response = self.client.post("/api/register/", payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.filter(username="testuser").exists())

	def test_user_login(self):
		User.objects.create_user(username="john", password="strongpass123")
		response = self.client.post(
			"/api/login/",
			{"username": "john", "password": "strongpass123"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)
