from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	list_display = ("id", "email" , "phone", "is_staff", "is_active", "created_at")
	list_display_links = ("email",)
	list_filter = ("is_staff", "is_superuser", "is_active", "groups")
	search_fields = ("email", "phone")
	ordering = ("-created_at",)
	readonly_fields = ("created_at",)

	fieldsets = (
		(None, {"fields": ("email", "password")}),
		("Personal info", {"fields": ( "phone", "first_name", "last_name")}),
		(
			"Permissions",
			{
				"fields": (
					"is_active",
					"is_staff",
					"is_superuser",
					"groups",
					"user_permissions",
				)
			},
		),
		("Important dates", {"fields": ("last_login", "date_joined", "created_at")}),
	)

	add_fieldsets = (
		(
			None,
			{
				"classes": ("wide",),
				"fields": ("email", "password1", "password2", "is_staff", "is_active"),
			},
		),
	)