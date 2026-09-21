import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)


def _verification_url(token):
    site = settings.ORBITE_SITE_URL.rstrip("/")
    return f"{site}/verification-email/{token}/"


def send_verification_email(user):
    """Generate a fresh token, persist it and send the confirmation email.

    Returns the token so tests/consumers can assert on it. The send itself is
    best-effort: a delivery failure never breaks registration — the token is
    kept so the user can request a new email later.
    """
    token = user.email_verification_token or get_random_string(32)
    user.email_verification_token = token
    user.email_verified = False
    user.save(update_fields=["email_verification_token", "email_verified"])

    url = _verification_url(token)
    subject = "Confirme ton adresse email — ORBITE"
    text = (
        f"Bonjour {user.full_name or user.username},\n\n"
        f"Merci pour ton inscription sur ORBITE. Il ne te reste qu'un clic "
        f"pour confirmer ton adresse email :\n\n{url}\n\n"
        f"Si tu n'es pas à l'origine de cette inscription, ignore ce message.\n\n"
        f"À bientôt,\nL'équipe ORBITE"
    )
    html = (
        "<p>Bonjour <strong>%(name)s</strong>,</p>"
        "<p>Merci pour ton inscription sur <strong>ORBITE</strong>. Il ne te "
        "reste qu'un clic pour confirmer ton adresse email :</p>"
        '<p style="margin:24px 0">'
        '<a href="%(url)s" style="background:#7C3AED;color:#fff;padding:12px 24px;'
        'border-radius:9999px;text-decoration:none;font-weight:bold">'
        "Confirmer mon adresse email</a></p>"
        "<p>Ou copie ce lien : <code>%(url)s</code></p>"
        "<p>Si tu n'es pas à l'origine de cette inscription, ignore ce message.</p>"
        "<p>À bientôt,<br>L'équipe ORBITE</p>"
    ) % {
        "name": user.full_name or user.username,
        "url": url,
    }

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.attach_alternative(html, "text/html")
        email.send(fail_silently=False)
    except Exception as exc:  # pragma: no cover - depends on SMTP availability
        logger.warning("Email de vérification non envoyé à %s : %s", user.email, exc)
    return token