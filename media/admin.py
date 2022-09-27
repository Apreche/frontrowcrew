from django.contrib import admin
from . import models


@admin.register(models.MP3)
class MP3Admin(admin.ModelAdmin):
    pass


@admin.register(models.FTPDestination)
class FTPDestinationAdmin(admin.ModelAdmin):
    pass
