from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import Profile, Role, User


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "phone",
            "xp",
            "level",
            "email_verified",
        ]
        read_only_fields = ["id", "role", "xp", "level", "email_verified"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "password2",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Les deux mots de passe ne correspondent pas."}
            )
        return attrs

    def create(self, validated):
        validated.pop("password2")
        password = validated.pop("password")
        user = User(**validated)
        user.set_password(password)
        user.role = User.ROLE_STUDENT
        user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "avatar",
            "bio",
            "language",
            "timezone",
            "theme",
            "learning_preferences",
            "notification_preferences",
            "ai_preferences",
        ]
        read_only_fields = ["id"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "label"]