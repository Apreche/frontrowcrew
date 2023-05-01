from django import http
from django import shortcuts
from django.db.models import F
from django.utils.translation import gettext as _
from django.contrib.postgres import search
from django.core.paginator import Paginator
from django.core import exceptions

from . import models


def homepage(request):
    """ The Homepage """
    template_name = "shows/homepage.html"
    context = {}
    return shortcuts.render(request, template_name, context)


def show_list(request):
    """ A page that lists all the published shows """
    template_name = "shows/show_list.html"
    shows = models.Show.published.all()
    if not shows:
        raise http.Http404(_("No published shows."))
    context = {
        "shows": shows
    }
    return shortcuts.render(request, template_name, context)


def show_detail(request, show_slug, tags=None):
    """ The page for a single show with its paginated content """
    ITEMS_PER_PAGE = 10
    template_name = "shows/show_detail.html"
    context = {}
    show = shortcuts.get_object_or_404(models.Show.published, slug=show_slug)
    content = show.published_content
    if tags is not None:
        tag_list = set(tags.split("+"))
        for tag in tag_list:
            content = content.filter(tags__slug__in=[tag])
        context.update({"tags": tag_list})
    paginator = Paginator(
        content,
        ITEMS_PER_PAGE,
        allow_empty_first_page=False,
    )
    if paginator.count == 0:
        raise http.Http404(_("Show has no content."))
    page_number = request.GET.get("page", "1")
    if not page_number.isnumeric():
        raise exceptions.BadRequest(_("Invalid Page Number"))
    page = paginator.get_page(
        int(page_number)
    )
    context.update(
        {
            "show": show,
            "page": page,
        }
    )
    return shortcuts.render(request, template_name, context)


def content_detail(request, show_slug, catalog_number, content_slug=None):
    """ The page for a single content item """
    template_name = "shows/content_detail.html"
    show = shortcuts.get_object_or_404(models.Show.published, slug=show_slug)
    content = shortcuts.get_object_or_404(
        show.published_content,
        catalog_number=catalog_number
    )
    if (content.slug != content_slug) or (show != content.show):
        return shortcuts.redirect(content, permanent=True)
    # Do not show similar content that is unpublished
    similar_content = models.Content.published.filter(
        id__in=[sc.id for sc in content.tags.similar_objects()]
    )
    context = {
        "content": content,
        "similar_content": similar_content,
    }
    return shortcuts.render(request, template_name, context)


def totd_list(request):
    """ A list of all the things of the day """
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
    """ Filter content by tag across all shows """
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
        allow_empty_first_page=False,
    )
    if paginator.count == 0:
        raise http.Http404(_("No content found with chosen tags."))
    page_number = request.GET.get("page", "1")
    if not page_number.isnumeric():
        raise exceptions.BadRequest(_("Invalid Page Number"))
    page = paginator.get_page(
        int(page_number)
    )
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
    results = models.Content.published.select_related(
        "show",
    ).annotate(
        search_rank=search.SearchRank(
            F("search_vector"), query
        )
    ).filter(
        search_vector=query
    ).order_by("-search_rank")
    paginator = Paginator(
        results,
        ITEMS_PER_PAGE,
        allow_empty_first_page=True,
    )
    page_number = request.GET.get("page", "1")
    if not page_number.isnumeric():
        raise exceptions.BadRequest(_("Invalid Page Number"))
    page = paginator.get_page(page_number)
    context = {
        "query": query_string,
        "page": page,
    }
    return shortcuts.render(request, template_name, context)
