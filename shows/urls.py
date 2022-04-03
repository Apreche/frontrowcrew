from django.urls import path

from . import feeds, views

urlpatterns = [
    path("<slug:show_slug>/", views.show_detail, name="show-detail"),
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
