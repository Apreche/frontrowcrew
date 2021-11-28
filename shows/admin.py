from django.contrib import admin

from . import models


class ShowAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Show, ShowAdmin)
