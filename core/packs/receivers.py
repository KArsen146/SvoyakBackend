from django.dispatch import receiver
from django.db import models

from core.packs.models import Pack, RoundInGame
from core.rooms.models import Room


@receiver(models.signals.post_delete, sender=Room)
def room_post_delete(sender, instance, *args, **kwargs):
    pack = Pack.objects.get(pk=instance.pack.id)
    if pack.is_deprecated and not pack.rooms_with_pack.count():
        print("Deleting pack because it is deprecated and no rooms with this pack")
        pack.delete()


#  TODO maybe add signal to change Room.cur_round when Round.cout_quets... = 0
# TODO maybe add signal to Round.cout_quets -- when Q.status = CA/WA
# @receiver(models.signals.post_save, sender=RoundInGame)
# def round_in_game_post_save(sender, instance, created=False, *args, **kwargs):
#     if created:
#         return
#     return
