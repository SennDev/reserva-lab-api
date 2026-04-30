from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response


class APIExceptionMixin:
    def handle_exception(self, exc):
        if isinstance(exc, PermissionError):
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        if isinstance(exc, DjangoValidationError):
            if hasattr(exc, "message_dict"):
                return Response(exc.message_dict, status=status.HTTP_400_BAD_REQUEST)
            return Response({"detail": exc.messages}, status=status.HTTP_400_BAD_REQUEST)

        return super().handle_exception(exc)
