from django import urls
from django.core.cache import cache

from . import models


def navigation(request):
    # Prevent context manager from running on admin pages
    # https://stackoverflow.com/a/44283845/65326
    if request.path.startswith(
        urls.reverse('admin:index')
    ):
        return {}

    global_nav_shows_list = cache.get_or_set(
        'global_nav_show_list',
        models.Show.published.filter(display_in_nav=True)
    )
    return {
        "nav_shows": global_nav_shows_list,
    }
