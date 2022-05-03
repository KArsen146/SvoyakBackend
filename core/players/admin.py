from django.contrib import admin
from .models import *


class PlayerAdmin(admin.ModelAdmin):
    fields = ('email', 'username', 'password', "is_verified")


admin.site.register(Player, PlayerAdmin)

