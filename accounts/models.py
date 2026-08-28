from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
	CUSTOMER = "customer", "Customer"
	SPECIALIST = "specialist", "Specialist"
	ADMIN = "admin", "Admin"
	OWNER = "owner", "Owner"


class User(AbstractUser):
	phone_number = models.CharField(max_length=20, blank=True)
	role = models.CharField(
		max_length=10,
		choices=UserRole.choices,
		default=UserRole.CUSTOMER,
	)

	def __str__(self):
		return self.username
