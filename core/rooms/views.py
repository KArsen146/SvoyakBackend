import jwt
from django.utils.decorators import method_decorator
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from core.rooms.models import Room
from .serializers import *
from rest_framework.decorators import action
from django.conf import settings
from django.core import serializers as django_serializers
from django.views import View
# from django.contrib.auth import get_user_model, authenticate
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from ..players.models import Player, PlayerInGame


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    def get_serializer_class(self):
        if self.action == 'list':
            return RoomShortSerializer
        return RoomSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = Player.objects.get(id=request.user.id)
        try:
            a = admin.player_in_room
        except:
            serializer.save(admin=admin)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        msg = 'Already in game'
        return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)


class LoginToRoomView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = LoginToRoomSerializer
    # serializer_class = RoomSerializer

    @property
    def allowed_methods(self):
        return ['post']

    def get_serializer_context(self):
        return {'request': self.request, 'format': self.format_kwarg, 'view': self}

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    @swagger_auto_schema(responses={
        '200': "'status': 'ok'",
        '403': 'Incorrect password/Already in game'})
    def post(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = serializer.validated_data['room']
        player = Player.objects.get(id=request.user.id)
        try:
            player_in_room = player.player_in_room
        except AttributeError as e:
            PlayerInGame.objects.create(room=room, player=player)  # TODO should we do it here?
            return Response(data={'status': 'ok'}, status=status.HTTP_200_OK)
        msg = 'Already in game'
        return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)


@swagger_auto_schema(responses={
        '200': "'status': 'ok'",
        '403': 'Not in this room/Do not have any room'})
class LogoutFromRoomView(APIView):
    @property
    def allowed_methods(self):
        return ['get']

    def get_serializer_class(self):
        pass

    def get(self, request, pk, format=None):
        response = Response()
        player = Player.objects.get(id=request.user.id)
        try:
            id = player.player_in_room.room.id
            if pk == id:
                player.player_in_room.delete()
                return response
            else:
                msg = 'Not in this room'
                return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)
        except:
            msg = 'Do not have any room'
            return Response({'detail': msg}, status=status.HTTP_403_FORBIDDEN)
