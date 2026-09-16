import secrets

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class CustomUserManager(UserManager):
	def _create_user(self, email, password, **extra_fields):
		if not email:
			raise ValueError("Email must be provided")
		email = self.normalize_email(email)
		username = (extra_fields.get("username") or email.split("@")[0]).strip() or "user"
		if self.model._default_manager.filter(username=username).exists():
			username = f"{username}-{secrets.token_hex(3)}"
		extra_fields["username"] = username
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username=None, email=None, password=None, **extra_fields):
		if email is None and username and "@" in str(username):
			email = username
			username = None
		elif email is None:
			email = username or extra_fields.pop("email", None)
			username = None
		if not email:
			raise ValueError("Email must be provided")
		extra_fields.setdefault("username", username or email.split("@")[0])
		extra_fields.setdefault("is_staff", False)
		extra_fields.setdefault("is_superuser", False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, username=None, email=None, password=None, **extra_fields):
		if email is None and username and "@" in str(username):
			email = username
			username = None
		elif email is None:
			email = username or extra_fields.pop("email", None)
			username = None
		if not email:
			raise ValueError("Email must be provided")
		extra_fields.setdefault("username", username or email.split("@")[0])
		extra_fields.setdefault("is_staff", True)
		extra_fields.setdefault("is_superuser", True)
		if extra_fields.get("is_staff") is not True:
			raise ValueError("Superuser must have is_staff=True.")
		if extra_fields.get("is_superuser") is not True:
			raise ValueError("Superuser must have is_superuser=True.")
		return self._create_user(email, password, **extra_fields)


class UserRole(models.TextChoices):
	CUSTOMER = "customer", "Customer"
	SPECIALIST = "specialist", "Specialist"
	ADMIN = "admin", "Admin"
	OWNER = "owner", "Owner"


class User(AbstractUser):
	email = models.EmailField(unique=True)
	phone_number = models.CharField(max_length=20, blank=True)
	role = models.CharField(
		max_length=10,
		choices=UserRole.choices,
		default=UserRole.CUSTOMER,
	)

	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = []

	objects = CustomUserManager()

	def __str__(self):
		return self.email
