from django.urls import path
from django.views.generic import base

from . import feeds, views

urlpatterns = [
    path("things/", views.totd_list, name="totd-list"),
    path("things/rss/", feeds.TotDFeed(), name="totd-list-rss",),
    path(
        "things/feed/",
        base.RedirectView.as_view(
            pattern_name="totd-list-rss",
            permanent=True,
        ),
        name="totd-feed-redirect"
    ),
    path(
        "things/feed/legacy/",
        base.RedirectView.as_view(
            pattern_name="totd-list-rss",
            permanent=True,
        ),
        name="totd-feed-legacy-redirect"
    ),
    path("<slug:show_slug>/", views.show_detail, name="show-detail"),
    path("<slug:show_slug>/tags/<str:tags>/", views.show_detail, name="show-tag-filter"),
    path("<slug:show_slug>/rss/", feeds.ShowFeed(), name="show-rss"),
    path("<slug:show_slug>/podcast-rss/", feeds.ShowPodcastFeed(), name="show-podcast-rss"),
    path(
        "<slug:show_slug>/<catalog_number>/",
        views.content_detail,
        {"content_slug": None},
        name="content-detail-noslug",
    ),
    path(
        "<slug:show_slug>/<catalog_number>/<slug:content_slug>/",
        views.content_detail,
        name="content-detail"
    ),
    path("", views.homepage, name="homepage"),
]
