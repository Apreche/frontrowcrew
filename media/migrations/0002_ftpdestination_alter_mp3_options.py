# Generated by Django 4.0.5 on 2022-06-14 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FTPDestination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('host', models.TextField()),
                ('username', models.TextField(blank=True, default='')),
                ('password', models.TextField(blank=True, default='')),
                ('directory', models.TextField(blank=True, default='')),
                ('custom_timeout', models.SmallIntegerField(blank=True, default=None)),
                ('url_prefix', models.TextField(blank=True, default='', help_text='The URL at which the file will be available after uploading.')),
            ],
        ),
        migrations.AlterModelOptions(
            name='mp3',
            options={'verbose_name': 'MP3', 'verbose_name_plural': 'MP3s'},
        ),
    ]
