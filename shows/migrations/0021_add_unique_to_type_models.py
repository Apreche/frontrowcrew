# Generated by Django 4.1.1 on 2022-12-29 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shows", "0020_populate_type_model_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="metadatatype",
            name="description",
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name="metadatatype",
            name="plural_description",
            field=models.TextField(default="", unique=True),
        ),
        migrations.AlterField(
            model_name="metadatatype",
            name="plural_slug",
            field=models.SlugField(default="", unique=True),
        ),
        migrations.AlterField(
            model_name="metadatatype",
            name="slug",
            field=models.SlugField(default="", unique=True),
        ),
        migrations.AlterField(
            model_name="relatedlinktype",
            name="description",
            field=models.TextField(unique=True),
        ),
        migrations.AlterField(
            model_name="relatedlinktype",
            name="plural_description",
            field=models.TextField(default="", unique=True),
        ),
        migrations.AlterField(
            model_name="relatedlinktype",
            name="plural_slug",
            field=models.SlugField(default="", unique=True),
        ),
        migrations.AlterField(
            model_name="relatedlinktype",
            name="slug",
            field=models.SlugField(default="", unique=True),
        ),
    ]
