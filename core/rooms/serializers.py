from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError
from django.contrib.auth import authenticate
from django.db import transaction

from .models import *
from core.players.serializers import PlayerSerializer, PlayerShortSerializer, PlayerInGameSerializer
from ..packs.models import Round, Question, Theme
from ..packs.serializers import RoundInGameSerializer
from ..players.models import Player


class RoomSerializer(ModelSerializer):
    players_in_room = PlayerInGameSerializer(read_only=True, many=True)
    # admin_id = serializers.IntegerField()

    def is_valid(self, raise_exception=False):
        res = super().is_valid(raise_exception)
        if not res:
            return res
        error = None
        if not Pack.objects.get(pk=self.validated_data['pack'].id):
            error = 'Pack with this id does not exist'
        if error and raise_exception:
            raise ValidationError(self.errors)
        return not bool(error)

    class Meta:
        model = Room
        fields = ['id', 'name', 'password', 'pack', 'players_in_room', 'document_id']
        # read_only_fields = ['admin']
        # fields = ['name', 'password', 'admin_id']
        extra_kwargs = {'password': {'write_only': True}}

    @transaction.atomic
    def create(self, validated_data):
        # admin_id = validated_data.pop('admin_id')
        admin = validated_data.pop('admin')
        room = super().create(validated_data)
        password = validated_data['password']
        room.set_password(password)
        # room.admin = Player.objects.get(id=admin_id)
        # room.save(update_fields=['password', 'admin'])
        room.save(update_fields=['password'])
        PlayerInGameSerializer._create(player=admin, room=room, is_room_admin=True, is_presenter=True)
        rounds = list(Round.objects.all().filter(pack=validated_data['pack']))
        rounds.reverse() #TODO мб можно лучше
        prev_round_in_game = None
        for i in rounds:
            prev_round_in_game = RoundInGameSerializer._create(round=i, next_round=prev_round_in_game)
        return room


class RoomShortSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name']


class LoginToRoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ['password']

    def validate(self, attrs):
        password = attrs['password']
        room = Room.objects.get(pk=self.context['view'].kwargs['pk'])

        if not room.check_password(password):
            raise PermissionDenied('Incorrect password')

        attrs['room'] = room
        return attrs
