from datetime import datetime

import jwt
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, AbstractUser
from django.conf import settings


class PlayerManager(BaseUserManager):
    """
    Custom player model manager where username is the unique identifiers
    for authentication.
    """

    def create_user(self, email, username, password, **extra_fields):
        """
        Create and save a Player with the given email and password.
        """
        # if not email:
        #     raise ValueError('The Email must be set')
        # email = self.normalize_email(email)
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
            raise ValueError(('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(('Superuser must have is_superuser=True.'))
        return self.create_user(email=email, username=username, password=password, **extra_fields)


class Player(AbstractUser):
    email = models.EmailField('Email address', db_index=True, max_length=64, unique=True)
    username = models.CharField(max_length=50, blank=False, null=False, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = PlayerManager()

    def generate_jwt_token(self):
        token = jwt.encode({
            'id': self.pk
        }, settings.SECRET_KEY, algorithm='HS256')

        return token


