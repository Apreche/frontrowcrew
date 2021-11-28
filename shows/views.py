from django.shortcuts import render
from . import models


def homepage(request):
    template_name = "shows/homepage.html"
    shows = models.Show.objects.all()
    context = {
        "shows": shows
    }
    return render(request, template_name, context)
