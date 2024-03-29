# Generated by Django 4.2.7 on 2023-11-11 02:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("shows", "0032_add_rendered_related_links"),
    ]

    operations = [
        migrations.CreateModel(
            name="Syndicator",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("shows", models.ManyToManyField(blank=True, to="shows.show")),
            ],
        ),
        migrations.CreateModel(
            name="Discourse",
            fields=[
                (
                    "syndicator_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="syndicators.syndicator",
                    ),
                ),
                ("url", models.URLField()),
                ("api_key", models.TextField()),
                ("username", models.TextField()),
                ("category_id", models.IntegerField()),
            ],
            bases=("syndicators.syndicator",),
        ),
    ]
