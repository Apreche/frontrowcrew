from django.urls import path

from . import views

urlpatterns = [
    path(
        "upload/",
        views.upload,
        name="creator-upload"
    ),
    path(
        "create_podcast/<int:mp3_id>/",
        views.create_podcast_episode,
        name="creator-podcast-episode"
    ),
]
