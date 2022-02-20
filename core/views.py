import jwt
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.conf import settings
# from django.contrib.auth import get_user_model, authenticate

from .models import *
from .serializers import *


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

        player = Player.objects.get(email=serializer.validated_data['email'])
        token = player.generate_jwt_token()
        response = Response(status=status.HTTP_201_CREATED)
        # response.set_cookie('access_token', token)

        return response


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    serializer_class = AuthByEmailPasswordSerializer

    @property
    def allowed_methods(self):
        return ['post']

    def get_serializer(self, *args, **kwargs):
        # kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        player = serializer.validated_data['player']
        token = jwt.encode({
            'id': player.id
        }, settings.SECRET_KEY, algorithm='HS256')

        response = Response(status.HTTP_200_OK)
        response.set_cookie('access_token', token)

        return response


class LogoutView(APIView):
    def get(self, request, format=None):
        request.auth.delete()

        response = Response()
        response.delete_cookie('access_token')
        return response
