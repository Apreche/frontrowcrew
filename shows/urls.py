from django.urls import path

from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("<slug:show_slug>/", views.show_detail, name="show-detail"),
    path(
        "<slug:show_slug>/<catalog_number>/",
        views.content_detail,
        {"content_slug": None},
        name="content-detail",
    ),
    path(
        "<slug:show_slug>/<catalog_number>/<slug:content_slug>/",
        views.content_detail,
        name="content-detail"
    ),
]
