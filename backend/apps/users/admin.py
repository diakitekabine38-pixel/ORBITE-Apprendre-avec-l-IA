from django.contrib import admin

from .models import Profile, Role, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_active", "is_staff")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("code", "label")


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "language", "timezone")