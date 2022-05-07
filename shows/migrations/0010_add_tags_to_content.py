# Generated by Django 4.0.4 on 2022-05-07 14:59

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0005_auto_20220424_2025'),
        ('shows', '0009_create_thing_of_the_day_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relatedlink',
            options={'ordering': ['-content__pub_time', 'author'], 'verbose_name': 'Related Link', 'verbose_name_plural': 'Related Links'},
        ),
        migrations.AddField(
            model_name='content',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]
