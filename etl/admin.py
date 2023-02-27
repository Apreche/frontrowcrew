from django import forms
from django.contrib import admin

from . import models


class ImportRecordForm(forms.ModelForm):
    class Meta:
        model = models.ImportRecord
        fields = "__all__"
        widgets = {
            "old_table_name": forms.TextInput,
            "new_table_name": forms.TextInput,
        }


@admin.register(models.ImportRecord)
class ImportRecordAdmin(admin.ModelAdmin):
    form = ImportRecordForm
    search_fields = (
        "old_id",
        "new_id",
    )
    readonly_fields = (
        "old_id",
        "old_table_name",
        "new_id",
        "new_table_name",
        "source_record",
    )
    list_display = (
        "id",
        "old_id",
        "old_table_name",
        "new_id",
        "new_table_name"
    )
    list_filter = (
        "old_table_name",
        "new_table_name",
    )
    ordering = ("id",)
