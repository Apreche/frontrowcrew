# Attempt to connect forum links to content

import datetime
import tqdm
import zoneinfo

from dateutil.parser import parse as dateparse

from django.db import connection
from django.db.models import Count

from etl import utils as etl_utils
from shows import models as show_models


class ForumETLDB:

    FORUM_ETL_DB_PATH = "etl/data/forum.db"
    OLD_FORUM_CUTOFF_DATE = dateparse('2016-12-23').date()
    OLD_FORUM_URL_TEMPLATE = "https://forum.frontrowcrew.com/index.php?p=/discussion/{id}/"
    NEW_FORUM_URL_TEMPLATE = "https://community.frontrowcrew.com/t/{id}/"

    OLD_FORUM_QUERY = """
        SELECT
            etl.id AS topic_id,
            (etl.created_at::timestamp)::date AS date,
            trim(etl.title) AS title,
            trim(etl.creator_name) AS username,
            trim(etl.category_name) AS category,
            CONCAT('https://forum.frontrowcrew.com/index.php?p=/discussion/', etl.id, '/') as url
        FROM frc_etl.oldforum AS etl
        WHERE (
            etl.title = %s
            OR etl.title = %s
            OR etl.title = %s
        )
    """

    NEW_FORUM_QUERY = """
        SELECT
            etl.id AS topic_id,
            (etl.created_at::timestamp at time zone 'America/New_York')::date AS date,
            trim(etl.title) AS title,
            trim(etl.creator_name) AS username,
            trim(etl.category_name) AS category,
            CONCAT('https://community.frontrowcrew.com/t/', etl.id, '/') as url
        FROM frc_etl.newforum AS etl
        WHERE (
            etl.title = %s
            OR etl.title = %s
            OR etl.title = %s
        )
    """

    MANUAL_LINK_QUERY = """
        SELECT
            content_id,
            show_title,
            content_title,
            forum,
            discussion_id
        FROM frc_etl.manual_forum_links
        ;
    """

    def __init__(self):
        self.cursor = connection.cursor()

    def __del__(self):
        self.cursor.close()

    def lookup(self, date, titles=[]):
        """ Find possible forum threads in the ETL DB """
        query = self.NEW_FORUM_QUERY
        if date <= self.OLD_FORUM_CUTOFF_DATE:
            query = self.OLD_FORUM_QUERY

        self.cursor.execute(query, [*titles])
        return etl_utils.dictfetchall(self.cursor)

    def manual_links(self):
        self.cursor.execute(self.MANUAL_LINK_QUERY)
        return etl_utils.dictfetchall(self.cursor)

    def one_old_thread_by_id(self, id):
        query = """
            SELECT * from frc_etl.oldforum where id = %s;
        """
        self.cursor.execute(query, [id])
        return etl_utils.dictfetchall(self.cursor)

    def one_new_thread_by_id(self, id):
        query = """
            SELECT * from frc_etl.newforum where id = %s;
        """
        self.cursor.execute(query, [id])
        return etl_utils.dictfetchall(self.cursor)


def run() -> None:
    forum_db = ForumETLDB()
    nytz = zoneinfo.ZoneInfo("America/New_York")

    for content in tqdm.tqdm(
        show_models.Content.objects.exclude(
            related_links__type_id=show_models.RelatedLinkType.FORUM_THREAD
        ),
        desc="Relinking Forum Threads"
    ):
        date = content.pub_time.astimezone(nytz).date()
        day_before = date - datetime.timedelta(days=1)
        day_after = date + datetime.timedelta(days=1)

        date_str = date.strftime("%y%m%d")
        titles = []
        titles.append(content.title)
        titles.append(f"GeekNights {date_str} - {content.title}")
        titles.append(f"GeekNights {content.show.title} - {content.title}")
        results = forum_db.lookup(date, titles)
        if len(results) == 0:
            continue

        date_filtered_results = [r for r in results if r["date"] == date]
        category_filtered_results = [r for r in results if r["category"] == "GeekNights"]
        username_filtered_results = [r for r in results if r["username"] in ("Apreche", "MrPeriod")]
        day_before_filtered_results = [r for r in results if r["date"] == day_before]
        day_after_filtered_results = [r for r in results if r["date"] == day_after]

        good_result = None
        for resultset in [
            results,
            date_filtered_results,
            category_filtered_results,
            username_filtered_results,
            day_before_filtered_results,
            day_after_filtered_results,
        ]:
            if len(resultset) == 1:
                good_result = resultset[0]
                break

        if good_result is not None:
            show_models.RelatedLink.objects.create(
                content=content,
                type_id=show_models.RelatedLinkType.FORUM_THREAD,
                title=good_result["title"],
                description=f"Forum discussion for {content.title}",
                url=good_result["url"],
                author="",
            )
        elif len(resultset) > 0:
            breakpoint()
            print(resultset)

    # Remove repeats
    repeats = show_models.RelatedLink.objects.filter(
        type_id=show_models.RelatedLinkType.FORUM_THREAD
    ).values(
        'url'
    ).annotate(
        total=Count(
            'url'
        )
    ).filter(
        total__gt=1
    )
    for repeat in repeats:
        url = repeat["url"]
        show_models.RelatedLink.objects.filter(
            url=url,
            type_id=show_models.RelatedLinkType.FORUM_THREAD
        ).delete()

    # Put in manual links
    manual_links = forum_db.manual_links()
    for link in manual_links:
        content = show_models.Content.objects.get(
            id=link["content_id"]
        )
        if link["forum"] == "Old Forum":
            discussion_id = link["discussion_id"]
            discussion = forum_db.one_old_thread_by_id(discussion_id)[0]
            discussion_title = discussion["title"]
            discussion_url = ForumETLDB.OLD_FORUM_URL_TEMPLATE.format(id=discussion_id)
        elif link["forum"] == "New Forum":
            discussion_id = link["discussion_id"]
            discussion = forum_db.one_new_thread_by_id(discussion_id)[0]
            discussion_title = discussion["title"]
            discussion_url = ForumETLDB.NEW_FORUM_URL_TEMPLATE.format(id=discussion_id)

        show_models.RelatedLink.objects.create(
            content=content,
            type_id=show_models.RelatedLinkType.FORUM_THREAD,
            title=discussion_title,
            description=f"Forum discussion for {content.title}",
            url=discussion_url,
            author="",
        )
