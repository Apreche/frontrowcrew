# Generated by Django 4.0.5 on 2022-06-18 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('podcasts', '0004_remove_unique_enclosure_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='podcast',
            name='custom_public_feed_url',
            field=models.URLField(
                blank=True,
                default='',
                help_text='The publicly shared RSS Feed URL for this podcast (i.e., FeedBurner)'
            ),
        ),
        migrations.AddField(
            model_name='podcastepisode',
            name='image',
            field=models.ImageField(
                blank=True,
                default='',
                height_field='image_height',
                upload_to='podcasts/podcastepisodes/image/',
                width_field='image_width'
            ),
        ),
        migrations.AddField(
            model_name='podcastepisode',
            name='image_description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='podcastepisode',
            name='image_height',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='podcastepisode',
            name='image_width',
            field=models.PositiveIntegerField(blank=True, default=None, null=True),
        ),
    ]
