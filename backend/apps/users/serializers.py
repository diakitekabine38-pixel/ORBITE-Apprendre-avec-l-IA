from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile, Role, User


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Connexion par email + mot de passe (le username reste accepté).

    SimpleJWT n'authentifie que par ``username`` : on accepte donc aussi un
    champ ``email``, que l'on résout vers le compte correspondant avant de
    déléguer la vérification du mot de passe au flux JWT classique. La
    réponse (jetons access/refresh) est identique.
    Le champ ``username`` reste accepté (rétrocompatibilité avec les tests).
    SimpleJWT redéclare ``username`` comme obligatoire dans ``__init__`` :
    on retire l'exigence après l'initialisation parente.
    """

    email = serializers.EmailField(required=False, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields["username"].required = False

    def validate(self, attrs):
        email = attrs.pop("email", None)
        if email and not attrs.get("username"):
            user = User.objects.filter(email__iexact=email).first()
            if not user:
                raise serializers.ValidationError(
                    {"email": "Aucun compte ne correspond à cette adresse."}
                )
            attrs["username"] = user.get_username()
        return super().validate(attrs)


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
    email = serializers.EmailField()

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
        existing = User.objects.filter(email__iexact=attrs["email"]).first()
        if existing and existing.email_verified:
            raise serializers.ValidationError(
                {"email": "Un compte actif utilise déjà cette adresse email."}
            )
        return attrs

    def create(self, validated):
        validated.pop("password2")
        password = validated.pop("password")
        email = validated.pop("email")
        # Un email jamais confirmé : on réutilise le compte existant pour ne
        # pas révéler son existence, on renouvelle les identifiants et on
        # renvoie un lien de vérification.
        user = (
            User.objects.filter(email__iexact=email, email_verified=False)
            .order_by("id")
            .first()
        )
        if user:
            for field, value in validated.items():
                setattr(user, field, value)
            user.email = email
            user.email_verified = False
            user.email_verification_token = ""
            user.is_active = False
            user.role = User.ROLE_STUDENT
            user.set_password(password)
            user.save()
            return user
        user = User(email=email, **validated)
        user.set_password(password)
        user.is_active = False
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