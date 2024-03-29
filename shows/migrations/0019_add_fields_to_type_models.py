# Generated by Django 4.1.1 on 2022-12-29 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shows", "0018_add_related_content_m2m"),
    ]

    operations = [
        migrations.AddField(
            model_name="metadatatype",
            name="plural_description",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="metadatatype",
            name="plural_slug",
            field=models.SlugField(default=""),
        ),
        migrations.AddField(
            model_name="metadatatype",
            name="slug",
            field=models.SlugField(default=""),
        ),
        migrations.AddField(
            model_name="relatedlinktype",
            name="plural_description",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="relatedlinktype",
            name="plural_slug",
            field=models.SlugField(default=""),
        ),
        migrations.AddField(
            model_name="relatedlinktype",
            name="slug",
            field=models.SlugField(default=""),
        ),
    ]
