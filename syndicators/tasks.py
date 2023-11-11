import celery

from shows import models as show_models
from syndicators import models as syndicator_models


@celery.shared_task
def syndicate(content_id, syndicator_id):
    """Syndicate content to just one destination"""
    syndicator = syndicator_models.Syndicator.objects.select_subclasses().get(
        id=syndicator_id
    )
    content = show_models.Content.objects.get(id=content_id)
    syndicator.syndicate(content)


@celery.shared_task
def full_syndication(content_id):
    """Syndicate content to all associated destinations"""
    show_id = show_models.Content.objects.values_list("show_id", flat=True).get(
        id=content_id
    )
    syndicator_ids = syndicator_models.Syndicator.shows.through.objects.filter(
        show_id=show_id
    ).values_list("syndicator_id", flat=True)

    syndicate_subtask = celery.subtask(syndicate)

    group = celery.group(
        syndicate_subtask.clone([content_id, syndicator_id])
        for syndicator_id in syndicator_ids
    )
    return group()
