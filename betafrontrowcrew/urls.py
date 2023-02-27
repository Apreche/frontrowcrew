"""betafrontrowcrew URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

# Update admin site headers
from django.utils.translation import gettext_lazy as _
admin.site.site_header = _("Front Row Crew CMS Admin")
admin.site.index_title = _("Front Row Crew CMS Admin")
admin.site.site_title = _("Front Row Crew CMS Admin")


urlpatterns = [
    path("", include("pagedown.urls")),
    path("admin/creator/", include("creator.urls")),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    path("", include("shows.urls")),
] + static(
    getattr(settings, "MEDIA_URL", "/media/"),
    document_root=getattr(settings, "MEDIA_ROOT", "/var/www/betafrontrowcrew/media/"),
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.insert(
        0,
        path("__debug__/", include(debug_toolbar.urls)),
    )
