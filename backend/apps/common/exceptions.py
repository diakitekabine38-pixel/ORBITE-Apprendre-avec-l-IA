from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework import status


def orbite_exception_handler(exc, context):
    """Normalise API errors into an ORBITE-friendly envelope.

    The spec forbids exposing raw technical status codes to learners; the API
    keeps a machine-readable `code` and a human `message`.
    """
    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    data = response.data
    return response