from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils.crypto import get_random_string

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsAdminUser, IsOwnerOrReadOnly

from .models import Profile, Role
from .serializers import (
    ChangePasswordSerializer,
    ProfileSerializer,
    RegisterSerializer,
    RoleSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data, status=status.HTTP_201_CREATED
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        user = User.objects.filter(email_verification_token=token).first()
        if not user:
            return Response(
                {"detail": "Lien de vérification invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.email_verified = True
        user.email_verification_token = ""
        user.save(update_fields=["email_verified", "email_verification_token"])
        return Response({"detail": "Email vérifié."})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Mot de passe actuel incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        return Response({"detail": "Mot de passe modifié."})


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.request.user.is_admin():
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        return queryset.get_or_create(user=self.request.user)[0]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get", "patch", "put"])
    def me(self, request):
        profile = self.get_object()
        if request.method == "GET":
            return Response(self.get_serializer(profile).data)
        serializer = self.get_serializer(
            profile, data=request.data, partial=request.method == "PATCH"
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    DEFAULT_ROLES = [
        ("student", "Apprenant"),
        ("instructor", "Formateur"),
        ("admin", "Administrateur"),
        ("super_admin", "Super administrateur"),
    ]

    def get_queryset(self):
        for code, label in self.DEFAULT_ROLES:
            Role.objects.get_or_create(code=code, defaults={"label": label})
        return Role.objects.all().order_by("id")