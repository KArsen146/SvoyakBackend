import jwt
from rest_framework import status, filters
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from django.conf import settings
from django.core import serializers as django_serializers
# from django.contrib.auth import get_user_model, authenticate

from .models import *
from .serializers import *
# from core.tasks import send_email_task


class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return PlayerShortSerializer
        return PlayerSerializer


class SignUpViewSet(CreateAPIView):
    model = Player
    permission_classes = [AllowAny,]
    serializer_class = PlayerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # send_email_task.delay('aboba')

        response = Response(data={'status': 'created'}, status=status.HTTP_201_CREATED)
        return response


class LoginView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = AuthByEmailPasswordSerializer

    def post(self, request):
        if not request.data and isinstance(request.user, Player):
            return Response(data={'email': request.user.email,
                                  'username': request.user.username,
                                  'current_room_id': request.user.current_room_id}, status=status.HTTP_200_OK) # TODO change this shit

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data

        token = jwt.encode({
            'id': data['id']
        }, settings.SECRET_KEY, algorithm='HS256')

        data.pop('id')
        data['access_token'] = token

        response = Response(data=data, status=status.HTTP_200_OK)
        # response.set_cookie('access_token', token, secure=True)
        # response.cookies['access_token']['samesite'] = None

        return response


class LogoutView(APIView):
    @property
    def allowed_methods(self):
        return ['get']

    def get(self, request, format=None):
        # request.auth.delete()

        response = Response()
        return response


class ResendVerificationLetter(GenericAPIView):
    permission_classes = [AllowAny, ]
    serializers = ResendVerificationLetterSerializer

    def get_serializer_class(self):
        return ResendVerificationLetterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = Response(data={'status': "Verification message was sent to your email"},
                            status=status.HTTP_200_OK)
        return response


class VerifyView(GenericAPIView):

    def get(self, request, verification_uuid):
        try:
            user = Player.objects.get(verification_uuid=verification_uuid)
        except Exception:
            return Response(data={'status': 'User does not exist'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_verified:
            return Response(data={'status': 'User is already verified'}, status=status.HTTP_403_FORBIDDEN)

        user.is_verified = True
        user.save()
        response = Response(data={'status': 'verified'}, status=status.HTTP_200_OK)
        return response


class ResetPassword(GenericAPIView):
    permission_classes = [AllowAny, ]
    serializers = ResetPasswordSerializer

    def get_serializer_class(self):
        return ResetPasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = Response(data={'status': "New password was sent in email"}, status=status.HTTP_200_OK)
        return response


class ChangePassword(GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializers = ChangePasswordSerializer

    def get_serializer_class(self):
        return ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        attrs = serializer.is_valid(raise_exception=True)
        response = Response(data={'status': "Password successfully changed"}, status=status.HTTP_200_OK)
        return response
