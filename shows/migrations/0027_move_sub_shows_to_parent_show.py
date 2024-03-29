# Generated by Django 4.1.7 on 2023-02-28 01:32

from django.db import migrations


def set_parent_shows(apps, schema_editor):
    # This will be a problem if a show is a sub show more than once
    # But I know we don't have that in our data right now
    # which is the reason we are making this change
    Show = apps.get_model("shows", "Show")
    for show in Show.objects.all():
        sub_shows = show.sub_shows.all()
        for sub_show in sub_shows:
            sub_show.parent_show = show
            sub_show.save()


def unset_parent_shows(apps, schema_editor):
    Show = apps.get_model("shows", "Show")
    Show.objects.all().update(parent_show=None)


class Migration(migrations.Migration):
    dependencies = [
        ("shows", "0026_add_parent_show_fk"),
    ]

    operations = [
        migrations.RunPython(
            set_parent_shows,
            unset_parent_shows,
        )
    ]
