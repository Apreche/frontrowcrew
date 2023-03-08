# Generated by Django 4.1.5 on 2023-02-16 00:52

from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):
    dependencies = [
        ("embeds", "0002_add_youtube_service"),
        ("taggit", "0005_auto_20220424_2025"),
        ("shows", "0023_content_embedded_media"),
    ]

    operations = [
        migrations.AlterField(
            model_name="content",
            name="embedded_media",
            field=models.ManyToManyField(blank=True, to="embeds.media"),
        ),
        migrations.AlterField(
            model_name="content",
            name="related_content",
            field=models.ManyToManyField(blank=True, to="shows.content"),
        ),
        migrations.AlterField(
            model_name="content",
            name="tags",
            field=taggit.managers.TaggableManager(
                blank=True,
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
