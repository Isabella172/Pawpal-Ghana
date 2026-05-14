from drf_spectacular.utils import extend_schema

from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer
)

def get_tokens_for_user(user):

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class RegisterView(APIView):

    permission_classes = [AllowAny]

    @extend_schema(
        request=RegisterSerializer,
        responses={201: RegisterSerializer},
    )
    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        tokens = get_tokens_for_user(user)

        return Response({
            'user': ProfileSerializer(user).data,
            'tokens': tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):

    permission_classes = [AllowAny]


    @extend_schema(
        request=LoginSerializer,
        responses={200: LoginSerializer},
    )
    def post(self, request):

        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        tokens = get_tokens_for_user(user)

        return Response({
            'user': ProfileSerializer(user).data,
            'tokens': tokens,
        })


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: ProfileSerializer},
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        request=ProfileSerializer,
        responses={200: ProfileSerializer},
    )
    def patch(self, request):
        return self.partial_update(request)

    def get_object(self):
        return self.request.user
