from procrastinate.contrib.django import app as procrastinate_app

from frontrowcrew.utils import tasks as task_utils
from shows import models as show_models
from syndicators import models as syndicator_models


@procrastinate_app.task
@task_utils.plug_psycopg_leak
def syndicate(content_id, syndicator_id):
    """Syndicate content to just one destination"""
    syndicator = syndicator_models.Syndicator.objects.select_subclasses().get(
        id=syndicator_id
    )
    content = show_models.Content.objects.get(id=content_id)
    syndicator.syndicate(content)
