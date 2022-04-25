# Generated by Django 4.0.2 on 2022-04-03 01:44

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='iTunesCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(default='', max_length=255)),
                ('subcategory_description', models.CharField(blank=True, default='', max_length=255)),
            ],
            options={
                'verbose_name': 'iTunes Category',
                'verbose_name_plural': 'iTunes Categories',
                'unique_together': {('description', 'subcategory_description')},
            },
        ),
        migrations.CreateModel(
            name='iTunesOwner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
            ],
            options={
                'verbose_name': 'iTunes Owner',
                'verbose_name_plural': 'iTunes Owners',
                'unique_together': {('name', 'email')},
            },
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=4000)),
                ('language', models.CharField(default='en', help_text='ISO 639-1', max_length=2)),
                ('managing_editor', models.EmailField(blank=True, default='', max_length=254)),
                ('web_master', models.EmailField(blank=True, default='', max_length=254)),
                ('ttl', models.PositiveIntegerField(default=None, null=True)),
                (
                    'image',
                    models.ImageField(
                        blank=True,
                        default='',
                        height_field='image_height',
                        upload_to='podcasts/podcast/image/',
                        width_field='image_width'
                    )
                ),
                ('image_height', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('image_width', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('image_description', models.TextField(blank=True, default='')),
                (
                    'itunes_image',
                    models.ImageField(
                        height_field='itunes_image_height',
                        upload_to='podcasts/podcast/itunes_image/',
                        width_field='itunes_image_width'
                    )
                ),
                ('itunes_image_height', models.PositiveIntegerField()),
                ('itunes_image_width', models.PositiveIntegerField()),
                ('itunes_explicit', models.BooleanField(default=None, null=True)),
                ('itunes_author', models.CharField(max_length=255)),
                (
                    'itunes_title',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text='Optional alternate feed title for iTunes',
                        max_length=255
                    )
                ),
                (
                    'itunes_type',
                    models.CharField(
                        blank=True,
                        choices=[
                            ('', 'Default'),
                            ('episodic', 'Episodic'),
                            ('serial', 'Serial')
                        ],
                        default='',
                        max_length=255
                    )
                ),
                (
                    'itunes_block',
                    models.BooleanField(
                        default=False,
                        help_text='Block directories from including this podcast.'
                    )
                ),
                (
                    'itunes_complete',
                    models.BooleanField(
                        default=False,
                        help_text='This podcast is DONE (will never have a new episode).'
                    )
                ),
                (
                    'itunes_new_feed_url',
                    models.URLField(
                        blank=True,
                        default='',
                        help_text='Use this for moving the podcast RSS URL'
                    )
                ),
                ('copyright', models.CharField(blank=True, default='', max_length=255)),
                ('creative_commons_license', models.URLField(blank=True, default='')),
                (
                    'itunes_owner',
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to='podcasts.itunesowner'
                    )
                ),
                (
                    'itunes_primary_category',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='podcasts.itunescategory'
                    )
                ),
                (
                    'itunes_secondary_category',
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='podcasts.itunescategory'
                    )
                ),
            ],
            options={
                'verbose_name': 'Podcast',
                'verbose_name_plural': 'Podcasts',
            },
        ),
        migrations.CreateModel(
            name='PodcastEnclosure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('length', models.PositiveBigIntegerField(help_text='Size of file in bytes')),
                (
                    'type',
                    models.CharField(
                        choices=[
                            ('audio/x-m4a', 'M4A'),
                            ('audio/mpeg', 'MP3'),
                            ('video/quicktime', 'MOV'),
                            ('video/mp4', 'MP4'),
                            ('video/x-m4v', 'M4V'),
                            ('application/pdf', 'PDF')
                        ],
                        default='audio/mpeg',
                        max_length=255
                    )
                ),
            ],
            options={
                'verbose_name': 'Podcast Enclosure',
                'verbose_name_plural': 'Podcast Enclosures',
            },
        ),
        migrations.CreateModel(
            name='PodcastEpisode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('guid', models.CharField(blank=True, default=uuid.uuid4, max_length=255)),
                ('guid_is_permalink', models.BooleanField(default=False)),
                ('pub_date', models.DateTimeField(blank=True, default=None)),
                ('description', models.TextField(blank=True, default='', max_length=4000)),
                ('duration', models.DurationField(blank=True, default=None, null=True)),
                ('author_name', models.CharField(blank=True, default='', max_length=255)),
                ('author_email', models.EmailField(blank=True, default='', max_length=254)),
                ('comments', models.URLField(blank=True, default='')),
                (
                    'itunes_image',
                    models.ImageField(
                        blank=True,
                        default='',
                        height_field='itunes_image_height',
                        upload_to='podcasts/podcastepisodes/itunes_image/',
                        width_field='itunes_image_width'
                    )
                ),
                ('itunes_image_height', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('itunes_image_width', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('itunes_explicit', models.BooleanField(default=None, null=True)),
                (
                    'itunes_title',
                    models.CharField(
                        blank=True,
                        default='',
                        help_text='Optional alternate episode title for iTunes',
                        max_length=255
                    )
                ),
                (
                    'itunes_episode_number',
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text='Episode Number, required for serial shows',
                        null=True
                    )
                ),
                (
                    'itunes_season_number',
                    models.PositiveIntegerField(
                        blank=True,
                        default=None,
                        help_text='Season Number',
                        null=True
                    )
                ),
                (
                    'itunes_episode_type',
                    models.CharField(
                        blank=True,
                        choices=[
                            ('', 'Default'),
                            ('full', 'Full'),
                            ('trailer', 'Trailer'),
                            ('bonus', 'Bonus')
                        ],
                        default='',
                        max_length=255
                    )
                ),
                (
                    'itunes_block',
                    models.BooleanField(
                        default=False,
                        help_text='Block directories from including this episode.'
                    )
                ),
                (
                    'enclosure',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to='podcasts.podcastenclosure'
                    )
                ),
                ('podcast', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='podcasts.podcast')),
            ],
            options={
                'verbose_name': 'Podcast Episode',
                'verbose_name_plural': 'Podcast Episodes',
            },
        ),
        migrations.CreateModel(
            name='PodcastChapter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.PositiveIntegerField()),
                ('end_time', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.CharField(blank=True, default='', max_length=255)),
                ('url', models.URLField(blank=True, default='')),
                (
                    'image',
                    models.ImageField(
                        blank=True,
                        default='',
                        height_field='image_height',
                        help_text='Aspect ratio must be 1:1.',
                        upload_to='podcasts/podcastchapters/image/',
                        width_field='image_width'
                    )
                ),
                ('image_height', models.PositiveIntegerField(blank=True, default=None, null=True)),
                ('image_width', models.PositiveIntegerField(blank=True, default=None, null=True)),
                (
                    'episode',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to='podcasts.podcastepisode'
                    )
                ),
            ],
            options={
                'verbose_name': 'Podcast Chapter',
                'verbose_name_plural': 'Podcast Chapters',
            },
        ),
        migrations.AddConstraint(
            model_name='podcastepisode',
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ('itunes_episode_number__isnull', False),
                    ('itunes_season_number__isnull', False),
                    _connector='OR'
                ),
                fields=(
                    'podcast',
                    'itunes_episode_number',
                    'itunes_season_number'
                ),
                name='unique_podcast_season_and_episode_when_set'
            ),
        ),
    ]