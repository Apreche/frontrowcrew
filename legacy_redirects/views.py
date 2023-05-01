import logging

from django import http as django_http
from django import urls as django_urls
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from taggit import models as taggit_models

from etl import models as etl_models
from shows import models as show_models

logger = logging.getLogger(__name__)


def geeknights_episode_detail_redirect(
    request,
    slug=None,
    year=None,
    month=None,
    day=None,
):
    """ Redirect very old content detail patterns """
    matching_content = show_models.Content.published.filter(
        Q(show__slug="geeknights") | Q(show__parent_show__slug="geeknights")
    ).filter(
        podcast_episode__isnull=False
    )
    if slug:
        import_record = etl_models.ImportRecord.objects.filter(
            old_table_name="podcast_episode",
            new_table_name="shows_content",
            source_record__old_slug=slug
        )
        if not import_record:
            raise django_http.Http404(_("No matching content"))
        matching_content = matching_content.filter(
            id__in=import_record.values("new_id")
        )
    if year:
        matching_content = matching_content.filter(pub_time__year=year)
    if month:
        matching_content = matching_content.filter(pub_time__month=month)
    if day:
        matching_content = matching_content.filter(pub_time__day=day)

    if len(matching_content) == 1:
        return redirect(matching_content.first())
    elif len(matching_content) > 1:
        visited_uri = request.build_absolute_uri()
        logger.warning(
            f"Ambiguous Redirect - {visited_uri}"
        )
    raise django_http.Http404(_("No matching content"))


def geeknights_episode_list_redirect(
    request,
    category,
    year=None,
    month=None,
):
    """ Redirect very old content list patterns """

    # construct query string for date filter
    date_dict = {
        "year": year,
        "month": month,
    }
    date_dict = {k: v for k, v in date_dict.items() if v is not None}
    date_querydict = django_http.QueryDict(mutable=True)
    date_querydict.update(date_dict)
    query_string = date_querydict.urlencode()

    # Rewrite some categories to include hyphens
    category_replacements = {
        "videogames": "video-games",
        "boardgames": "board-games",
    }
    if category in category_replacements:
        category = category_replacements[category]

    try:
        # Redirect if category matches a show slug
        show = show_models.Show.objects.get(slug=category)
        url = show.get_absolute_url() + query_string
        return redirect(url)
    except show_models.Show.DoesNotExist:
        pass

    try:
        # Redirect if category matches a tag
        taggit_models.Tag.objects.get(slug=category)
        url = django_urls.reverse(
            "tag-filter",
            kwargs={
                "tags": category,
            }
        ) + query_string
        return redirect(url)
    except taggit_models.Tag.DoesNotExist:
        pass

    raise django_http.Http404(_("No matching show"))


def news_detail_redirect(
    request,
    slug=None,
    year=None,
    month=None,
    day=None,
):
    """ Redirect a very old news content detail pattern """
    matching_content = show_models.Content.published.filter(
        show__slug="news"
    ).filter(
        pub_time__year=year,
        pub_time__month=month,
        pub_time__day=day,
    )
    if slug is not None:
        import_record = etl_models.ImportRecord.objects.filter(
            old_table_name="news_news",
            new_table_name="shows_content",
            source_record__old_slug=slug
        )
        if not import_record:
            raise django_http.Http404(_("No matching content"))
        matching_content = matching_content.filter(
            id__in=import_record.values("new_id")
        )
    if len(matching_content) == 1:
        return redirect(matching_content.first())
    elif len(matching_content) > 1:
        visited_uri = request.build_absolute_uri()
        logger.warning(
            f"Ambiguous Redirect - {visited_uri}"
        )
    raise django_http.Http404(_("No matching content"))
