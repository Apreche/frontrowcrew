from django.urls import path

from . import feeds

urlpatterns = [
    path("<int:podcast_id>/rss.xml", feeds.PodcastFeed(), name="podcast-rss"),
]
