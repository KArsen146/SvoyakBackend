import jwt
import uuid
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser, User
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from core.rooms.models import Room


class PlayerManager(BaseUserManager):
    """
    Custom player model manager where username is the unique identifiers
    for authentication.
    """

    def create_user(self, email, username, password, **extra_fields):
        """
        Create and save a Player with the given email and password.
        """
        player = self.model(username=username, email=email, **extra_fields)
        player.set_password(password)
        player.save()
        return player

    def create_superuser(self, email, username, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email=email, username=username, password=password, **extra_fields)


class Player(AbstractUser):
    email = models.EmailField('email', db_index=True, max_length=64, unique=True)
    username = models.CharField(max_length=50, blank=False, null=False, unique=True, db_index=True)
    # current_room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True)
    is_verified = models.BooleanField('verified', default=False)
    verification_uuid = models.UUIDField('Unique Verification UUID', default=uuid.uuid4)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = PlayerManager()

    def __str__(self):
        return self.username

    def generate_jwt_token(self):
        token = jwt.encode({
            'id': self.pk
        }, settings.SECRET_KEY, algorithm='HS256')

        return token

    # @classmethod
    # def resolve_jwt(cls, token) -> dict:
    #     payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')
    #     return payload

    @classmethod
    def get_by_jwt(cls, token):
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms='HS256')

        if 'id' not in payload:
            return None

        return cls.objects.get(id=payload['id'])

    @property
    def current_room_id(self):
        try:
            return self.player_in_room.room.id
        except:
            return None


class PlayerInGame(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE, primary_key=True, related_name="player_in_room")
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=False, related_name="players_in_room", db_index=True)
    is_room_admin = models.BooleanField(_('room admin status'), default=False)
    is_presenter = models.BooleanField(_('room presenter status'), default=False)
    score = models.IntegerField(default=0, null=False)

    def __str__(self):
        return self.player.username
