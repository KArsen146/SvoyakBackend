from django.contrib import admin
from .models import *


class PackAdmin(admin.ModelAdmin):
    fields = ('title', 'author')


admin.site.register(Pack, PackAdmin)
