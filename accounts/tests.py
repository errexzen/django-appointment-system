from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class AuthAPITests(APITestCase):
	def test_user_registration(self):
		payload = {
			"email": "test@example.com",
			"phone_number": "09120000000",
			"first_name": "Test",
			"last_name": "User",
			"password": "strongpass123",
			"accept_terms": True,
			"accept_privacy": True,
		}
		response = self.client.post("/api/register/", payload, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(User.objects.filter(email="test@example.com").exists())

	def test_user_login(self):
		User.objects.create_user(email="john@example.com", password="strongpass123")
		response = self.client.post(
			"/api/login/",
			{"email": "john@example.com", "password": "strongpass123"},
			format="json",
		)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)

	def test_profile_update_without_email_keeps_existing_email(self):
		user = User.objects.create_user(email="keep@example.com", password="strongpass123")
		self.client.force_authenticate(user)
		response = self.client.patch(
			"/api/profile/",
			{"first_name": "Updated", "phone_number": "09120000000"},
			format="json",
		)
		self.assertEqual(response.status_code, 200, response.data)
		user.refresh_from_db()
		self.assertEqual(user.email, "keep@example.com")
		self.assertEqual(user.first_name, "Updated")

	def test_profile_update_with_new_valid_email_succeeds(self):
		user = User.objects.create_user(email="old@example.com", password="strongpass123")
		self.client.force_authenticate(user)
		response = self.client.patch(
			"/api/profile/",
			{"email": "new@example.com", "last_name": "Changed"},
			format="json",
		)
		self.assertEqual(response.status_code, 200, response.data)
		user.refresh_from_db()
		self.assertEqual(user.email, "new@example.com")
		self.assertEqual(user.last_name, "Changed")

	def test_profile_update_rejects_duplicate_email(self):
		other = User.objects.create_user(email="other@example.com", password="strongpass123")
		user = User.objects.create_user(email="current@example.com", password="strongpass123")
		self.client.force_authenticate(user)
		response = self.client.patch(
			"/api/profile/",
			{"email": other.email},
			format="json",
		)
		self.assertEqual(response.status_code, 400, response.data)
		user.refresh_from_db()
		self.assertEqual(user.email, "current@example.com")

	def test_registration_requires_email(self):
		payload = {
			"phone_number": "09120000000",
			"password": "strongpass123",
			"accept_terms": True,
			"accept_privacy": True,
		}
		response = self.client.post("/api/register/", payload, format="json")
		self.assertEqual(response.status_code, 400, response.data)
		self.assertIn("email", response.data)
