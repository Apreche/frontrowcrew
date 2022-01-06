from . import models

def navlinks_renderer(request):
    return {
        "shows" : models.Show.objects.all()
    }
