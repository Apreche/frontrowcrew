from django.db import migrations
from django.utils.translation import gettext_lazy as _

from shows import models


def create_related_link_types(apps, schema_editor):
    RelatedLinkType = apps.get_model("shows", "RelatedLinkType")
    RelatedLinkType.objects.create(
        id=models.RelatedLinkType.BLUESKY_POST,
        description=_("Bluesky Post"),
        plural_description=_("Bluesky Posts"),
        slug="bluesky_chat",
        plural_slug="bluesky_chats",
    )


def delete_related_link_types(apps, schema_editor):
    RelatedLinkType = apps.get_model("shows", "RelatedLinkType")
    RelatedLinkType.objects.filter(
        id=models.RelatedLinkType.BLUESKY_POST,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("shows", "0033_add_discord_related_link_type"),
    ]

    operations = [
        migrations.RunPython(
            create_related_link_types,
            delete_related_link_types,
        ),
        migrations.RunSQL(
            sql=[
                (
                    "ALTER sequence shows_relatedlinktype_id_seq RESTART with %s;",
                    [models.RelatedLinkType.BLUESKY_POST + 1],
                ),
            ],
            reverse_sql=[
                (
                    "ALTER sequence shows_relatedlinktype_id_seq RESTART with %s;",
                    [models.RelatedLinkType.BLUESKY_POST],
                )
            ],
        ),
    ]
