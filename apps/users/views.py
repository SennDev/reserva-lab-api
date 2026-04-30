from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.serializers import (
    CurrentUserUpdateSerializer,
    LogoutSerializer,
    RegisterSerializer,
    ReservaLabTokenObtainPairSerializer,
    UserSerializer,
)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = ReservaLabTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "Usuario registrado correctamente.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CurrentUserView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserSerializer
        return CurrentUserUpdateSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh_token = serializer.validated_data["refresh"]
        token = self.get_token(refresh_token)
        token.blacklist()
        return Response({"message": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)

    @staticmethod
    def get_token(refresh_token):
        from rest_framework_simplejwt.tokens import RefreshToken

        return RefreshToken(refresh_token)

# Create your views here.
