# Generated by Django 4.1.7 on 2023-02-27 03:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shows", "0024_content_manytomany_fields_optional"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="content",
            options={
                "get_latest_by": "pub_time",
                "ordering": ["-pub_time"],
                "verbose_name": "Content",
                "verbose_name_plural": "Content",
            },
        ),
        migrations.AlterModelOptions(
            name="relatedlinktype",
            options={
                "verbose_name": "Related Link Type",
                "verbose_name_plural": "Related Link Types",
            },
        ),
    ]