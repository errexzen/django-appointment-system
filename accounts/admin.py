from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	list_display = ("id", "username", "email", "phone_number", "is_staff", "is_active")
	list_filter = ("is_staff", "is_active", "is_superuser")
	search_fields = ("username", "email", "phone_number")
	fieldsets = UserAdmin.fieldsets + (("Additional Info", {"fields": ("phone_number",)}),)
