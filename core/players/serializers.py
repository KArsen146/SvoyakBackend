from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, NotFound, ParseError
from django.contrib.auth import authenticate
from django.db import transaction

from .email import send_new_password_email, send_verification_email
from .models import *


class PlayerShortSerializer(ModelSerializer):
    class Meta:
        model = Player
        fields = ['username']


class PlayerInGameSerializer(ModelSerializer):
    player = PlayerShortSerializer(read_only=True)

    @classmethod
    def _create(cls, player, room, is_room_admin=False, is_presenter=False, score=0):
        player_in_game = PlayerInGame.objects.create(player=player, room=room, is_room_admin=is_room_admin,
                                                     is_presenter=is_presenter, score=score)
        return player_in_game

    class Meta:
        model = PlayerInGame
        fields = ['player', 'room', 'is_room_admin', 'is_presenter', 'score']
        extra_kwargs = {'player': {'read_only': True}}


class PlayerSerializer(ModelSerializer):
    player_in_room = PlayerInGameSerializer(read_only=True)

    class Meta:
        model = Player
        fields = ['email', 'username', 'password', 'player_in_room']
        extra_kwargs = {'password': {'write_only': True}, 'player_in_room': {'read_only': True}}

    def create(self, validated_data):
        with transaction.atomic():
            player = super().create(validated_data)
            password = validated_data['password']
            player.set_password(password)
            player.save(update_fields=['password'])

        return player


class AuthByEmailPasswordSerializer(ModelSerializer):
    email = serializers.EmailField(max_length=64)

    class Meta:
        model = Player
        fields = ['id', 'username', 'email', 'password', 'current_room_id']
        read_only_fields = ['username', 'current_room_id']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        player = authenticate(request=self.context.get('request'), email=email, password=password)

        if not player:
            msg = 'Unable to log in with provided credentials.'
            raise NotAuthenticated(msg, 'authorization')

        if not player.is_verified:
            msg = 'User is not verified'
            raise PermissionDenied(msg)

        attrs['id'] = player.id
        attrs['username'] = player.username
        attrs['current_room_id'] = player.current_room_id

        return attrs


class ResendVerificationLetterSerializer(Serializer):
    email = serializers.EmailField(max_length=64)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email', '')
        try:
            user = Player.objects.get(email=email)
        except Exception:
            msg = 'No user with this email address'
            raise NotAuthenticated(msg)
        if user.is_verified:
            msg = 'User is already verified'
            raise PermissionDenied(msg)
        send_verification_email(email, user.verification_uuid)
        return super().validate(attrs)


class ResetPasswordSerializer(Serializer):
    email = serializers.EmailField(max_length=64)

    class Meta:
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email', '')
        try:
            user = Player.objects.get(email=email)
        except Exception:
            msg = 'No user with this email address'
            raise NotAuthenticated(msg)
        password = Player.objects.make_random_password()
        user.set_password(password)
        user.save()
        send_new_password_email(email, password)
        return super().validate(attrs)


class ChangePasswordSerializer(Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)
    repeat_password = serializers.CharField(max_length=128)

    class Meta:
        fields = ['old_password', 'new_password', 'repeat_password']

    def validate(self, attrs):
        old_password = attrs.get('old_password', '')
        new_password = attrs.get('new_password', '')
        repeat_password = attrs.get('repeat_password', '')
        user = self.context.get('request').user
        if not user.check_password(old_password):
            msg = 'Old password is incorrect'
            raise PermissionDenied(msg)
        if new_password != repeat_password:
            msg = 'Passwords do not match'
            raise ParseError(msg)
        user.set_password(new_password)
        user.save()
        return super().validate(attrs)
