# Generated by Django 4.1.1 on 2022-11-04 23:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ImportRecord",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("import_time", models.DateTimeField(auto_now_add=True)),
                ("old_id", models.BigIntegerField()),
                ("old_table_name", models.TextField()),
                ("new_id", models.BigIntegerField()),
                ("new_table_name", models.TextField()),
                ("source_record", models.JSONField()),
            ],
        ),
    ]