from django.contrib import admin

from . import models


class ShowAdmin(admin.ModelAdmin):
    pass


class ContentAdmin(admin.ModelAdmin):
    raw_id_fields = ("show",)


admin.site.register(models.Show, ShowAdmin)
admin.site.register(models.Content, ContentAdmin)
