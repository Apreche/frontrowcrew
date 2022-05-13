# Generated by Django 4.0.4 on 2022-05-03 01:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shows', '0007_change_show_podcast_to_one_to_one'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelatedLinkType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='show',
            name='sub_shows',
            field=models.ManyToManyField(blank=True, to='shows.show', verbose_name='Sub-shows'),
        ),
        migrations.CreateModel(
            name='RelatedLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField()),
                ('description', models.TextField(blank=True, default="")),
                ('url', models.URLField()),
                ('author', models.TextField()),
                ('error', models.BooleanField(default=False)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shows.content')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='shows.relatedlinktype')),
            ],
            options={
                'verbose_name': 'Related Link',
                'verbose_name_plural': 'Related Links',
                'ordering': ['-content__pub_time', 'title'],
            },
        ),
    ]
