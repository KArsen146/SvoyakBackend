from django.dispatch import receiver
from django.db import models, transaction

from core.players.email import send_verification_email
from core.players.models import PlayerInGame, Player
from core.rooms.models import Room


@receiver(models.signals.post_delete, sender=PlayerInGame)
def player_in_room_pre_delete(sender, instance, *args, **kwargs):
    with transaction.atomic():
        if instance.is_room_admin and Room.objects.get(pk=instance.room.id):
            print("Deleting room because admin lives it")
            Room.objects.get(pk=instance.room.id).delete()


@receiver(models.signals.post_save, sender=Player)
def user_post_save(sender, instance, created=False, *args, **kwargs):
    if not instance.is_verified and created:
        print("Creating task send verification letter")
        send_verification_email(instance.email, instance.verification_uuid)
