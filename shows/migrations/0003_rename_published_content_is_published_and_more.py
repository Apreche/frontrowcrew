# Generated by Django 4.0 on 2022-01-07 02:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0002_alter_show_slug_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='content',
            old_name='published',
            new_name='is_published',
        ),
        migrations.AddField(
            model_name='show',
            name='is_published',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='show',
            name='pub_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]