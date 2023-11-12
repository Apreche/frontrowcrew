import re

from django import http, shortcuts
from django.contrib.postgres import search
from django.core.paginator import Paginator
from django.db.models import F, Prefetch
from django.utils.translation import gettext as _

from . import models


def homepage(request):
    """The Homepage"""
    template_name = "shows/homepage.html"

    try:
        latest_book_club = (
            models.Content.published.filter(show__slug="book-club")
            .filter(podcast_episode__isnull=True)
            .select_related(
                "show",
                "podcast_episode",
            )
            .only(
                "show",
                "catalog_number",
                "slug",
                "title",
                "pub_time",
                "rendered_html",
                "podcast_episode",
            )
            .latest()
        )
    except models.Content.DoesNotExist:
        latest_book_club = None

    try:
        latest_news = (
            models.Content.published.filter(show__slug="news")
            .select_related(
                "show",
                "podcast_episode",
            )
            .latest()
        )
    except models.Content.DoesNotExist:
        latest_news = None

    try:
        latest_contents = models.Content.published.all()
        if latest_book_club:
            latest_contents = latest_contents.exclude(id=latest_book_club.id)
        if latest_news:
            latest_contents = latest_contents.exclude(id=latest_news.id)
        latest_content = (
            latest_contents.select_related(
                "show",
                "podcast_episode",
                "podcast_episode__enclosure",
            )
            .prefetch_related(
                "embedded_media",
            )
            .latest()
        )
    except models.Content.DoesNotExist:
        latest_content = None

    context = {
        "latest_content": latest_content,
        "latest_book": latest_book_club,
        "latest_news": latest_news,
    }
    return shortcuts.render(request, template_name, context)


def show_list(request):
    """A page that lists all the published shows"""
    template_name = "shows/show_list.html"
    shows = models.Show.published.all()
    if not shows:
        raise http.Http404(_("No published shows."))
    context = {"shows": shows}
    return shortcuts.render(request, template_name, context)


# AKA: content_list
def show_detail(request, show_slug, tags=None):
    """The page for a single show with its paginated content"""
    ITEMS_PER_PAGE = 9
    template_name = "shows/show_detail.html"
    context = {}
    show = shortcuts.get_object_or_404(
        models.Show.published.select_related("podcast"), slug=show_slug
    )
    content = show.published_content.prefetch_related(
        "tags",
    )
    if tags is not None:
        tag_list = set(tags.split("+"))
        for tag in tag_list:
            content = content.filter(tags__slug__in=[tag])
        context.update({"tags": tag_list})

    # query parameter year month filter
    year = request.GET.get("year", None)
    if year is not None and re.match(r"^\d{4}$", year):
        content = content.filter(pub_time__year=year)
    month = request.GET.get("month", None)
    if month is not None and re.match(r"^(0?[1-9]|1[012])$", month):
        content = content.filter(pub_time__month=month)

    try:
        latest_content = (
            content.select_related(
                "show",
                "podcast_episode",
                "podcast_episode__enclosure",
            )
            .prefetch_related(
                "tags",
                "embedded_media",
            )
            .latest()
        )
    except models.Content.DoesNotExist:
        latest_content = None

    for related_link in models.RelatedLink.published.filter(
        content=latest_content
    ).select_related("type"):
        type_string = f"latest_{related_link.type.plural_slug}"
        context.setdefault(type_string, [])
        context[type_string].append(related_link)

    paginated_content = content
    if latest_content:
        paginated_content = paginated_content.exclude(id=latest_content.id)

    paginator = Paginator(
        paginated_content,
        ITEMS_PER_PAGE,
    )
    page_number = request.GET.get("page", "1")
    page = paginator.get_page(int(page_number))
    context.update(
        {
            "show": show,
            "page": page,
        }
    )
    if not page.has_previous():
        context.update(
            {
                "latest_content": latest_content,
            }
        )
    return shortcuts.render(request, template_name, context)


def content_detail(request, show_slug, catalog_number, content_slug=None):
    """The page for a single content item"""
    template_name = "shows/content_detail.html"
    context = {}
    show = shortcuts.get_object_or_404(models.Show.published, slug=show_slug)
    content = shortcuts.get_object_or_404(
        show.published_content.select_related(
            "show",
            "podcast_episode",
            "podcast_episode__enclosure",
        ).prefetch_related(
            "tags",
            "embedded_media",
        ),
        catalog_number=catalog_number,
    )
    if (content.slug != content_slug) or (show != content.show):
        return shortcuts.redirect(content, permanent=True)

    for related_link in models.RelatedLink.published.filter(
        content=content
    ).select_related("type"):
        type_string = related_link.type.plural_slug
        context.setdefault(type_string, [])
        context[type_string].append(related_link)

    # Do not show similar content that is unpublished
    # similar_content = models.Content.published.filter(
    #     id__in=[sc.id for sc in content.tags.similar_objects()]
    # )
    context.update(
        {
            "content": content,
            "show": show,
            # "similar_content": similar_content,
        }
    )
    return shortcuts.render(request, template_name, context)


def totd_list(request):
    """A list of all the things of the day"""
    template_name = "shows/totd_list.html"
    things_of_the_day = models.RelatedLink.published.filter(
        type_id=models.RelatedLinkType.THING_OF_THE_DAY
    )
    if not things_of_the_day:
        raise http.Http404(_("No Things of the Day found."))
    context = {
        "things_of_the_day": things_of_the_day,
    }
    return shortcuts.render(request, template_name, context)


def tag_filter(request, tags):
    """Filter content by tag across all shows"""
    ITEMS_PER_PAGE = 10
    template_name = "shows/tag_filter.html"
    context = {}
    content = models.Content.published.all()
    tag_list = set(tags.split("+"))
    for tag in tag_list:
        content = content.filter(tags__slug__in=[tag])
    context.update({"tags": tag_list})
    paginator = Paginator(
        content,
        ITEMS_PER_PAGE,
    )
    page_number = request.GET.get("page", "1")
    page = paginator.get_page(int(page_number))
    context.update(
        {
            "page": page,
        }
    )
    return shortcuts.render(request, template_name, context)


def content_search(request):
    ITEMS_PER_PAGE = 10
    template_name = "shows/search_results.html"
    query_string = request.GET.get("q", "")
    query = search.SearchQuery(query_string, search_type="websearch")
    forum_threads = models.RelatedLink.published.filter(
        type=models.RelatedLinkType.FORUM_THREAD
    )
    results = (
        models.Content.published.select_related(
            "show",
        )
        .prefetch_related(
            "tags",
            Prefetch(
                "related_links",
                queryset=forum_threads,
                to_attr="forum_threads",
            ),
        )
        .annotate(search_rank=search.SearchRank(F("search_vector"), query))
        .filter(search_vector=query)
        .order_by("-search_rank")
    )
    paginator = Paginator(
        results,
        ITEMS_PER_PAGE,
    )
    page_number = request.GET.get("page", "1")
    page = paginator.get_page(page_number)
    context = {
        "query": query_string,
        "page": page,
    }
    return shortcuts.render(request, template_name, context)
