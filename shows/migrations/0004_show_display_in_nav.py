# Generated by Django 4.0 on 2022-01-08 00:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0003_rename_published_content_is_published_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='display_in_nav',
            field=models.BooleanField(default=False),
        ),
    ]
