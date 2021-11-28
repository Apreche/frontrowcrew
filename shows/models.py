from django.db import models

class Show(models.Model):
    title = models.TextField()
    slug = models.SlugField()
    logo = models.ImageField(upload_to="show/logos/")
    thumbnail = models.ImageField(upload_to="show/thumbnails/")

    def __str__(self):
        return self.title
