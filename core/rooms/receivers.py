import channels.layers
from asgiref.sync import async_to_sync

from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.db import transaction

# from core.players.models import *
from core.rooms.models import *


@receiver(signal=post_delete, sender=Room, dispatch_uid='update_rooms_in_lobby_on_delete')
@receiver(signal=post_save, sender=Room, dispatch_uid='update_rooms_in_lobby_on_create')
def update_rooms_in_lobby(sender, instance, *args, **kwargs):
    transaction.on_commit(lambda: __update_rooms_in_lobby(sender, instance, **kwargs))


def __update_rooms_in_lobby(sender, instance, **kwargs):
    if 'created' not in kwargs or kwargs['created'] or (kwargs['update_fields'] is not None and 'name' in kwargs['update_fields']):
        channel_layer = channels.layers.get_channel_layer()

        rooms = Room.get_all_room_names()
        # print(channel_layer.groups)
        async_to_sync(channel_layer.group_send)(
            'lobby',
            {
                'type': 'send_updates',
                'message': rooms
            }
        )
