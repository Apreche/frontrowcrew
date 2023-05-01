from django.urls import path

from . import feeds, views

urlpatterns = [
    path("shows/", views.show_list, name="show-list"),
    path("search/", views.content_search, name="content-search"),
    path("things/", views.totd_list, name="totd-list"),
    path(
        "things/rss/",
        feeds.TotDFeed(),
        name="totd-rss",
    ),
    path("tags/<str:tags>/", views.tag_filter, name="tag-filter"),
    path("<slug:show_slug>/", views.show_detail, name="show-detail"),
    path(
        "<slug:show_slug>/tags/<str:tags>/", views.show_detail, name="show-tag-filter"
    ),
    path("<slug:show_slug>/rss/", feeds.ShowFeed(), name="show-rss"),
    path(
        "<slug:show_slug>/podcast-rss/",
        feeds.ShowPodcastFeed(),
        name="show-podcast-rss",
    ),
    path(
        "<slug:show_slug>/<catalog_number>/",
        views.content_detail,
        {"content_slug": None},
        name="content-detail-noslug",
    ),
    path(
        "<slug:show_slug>/<catalog_number>/<slug:content_slug>/",
        views.content_detail,
        name="content-detail",
    ),
    path("", views.homepage, name="homepage"),
]
