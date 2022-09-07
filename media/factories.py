import factory
import os

from . import models


class MP3Factory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MP3
        exclude = (
            "filename",
        )

    filename = factory.Faker("file_name", extension="mp3")
    file = factory.django.FileField(
        from_path=os.path.join(
            os.path.dirname(__file__),
            "tests/data/test_podcast.mp3"
        ),
        filename=factory.SelfAttribute("..filename")
    )


class FTPDestinationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FTPDestination
        exclude = (
            "has_username",
            "has_password",
            "has_directory",
            "has_custom_timeout",
            "directory_path",
            "has_url_prefix",

        )

    name = factory.Faker("company")
    host = factory.Faker("hostname")
    has_username = factory.Faker("boolean")
    username = factory.Maybe(
        "has_username",
        factory.Faker("user_name"),
        ""
    )
    has_password = factory.Faker("boolean")
    password = factory.Maybe(
        "has_password",
        factory.Faker("password"),
        ""
    )
    directory_path = factory.Faker("file_path")
    has_directory = factory.Faker("boolean")
    directory = factory.Maybe(
        "has_directory",
        factory.LazyAttribute(
            lambda o: os.path.dirname(o.directory_path)
        ),
        ""
    )
    has_custom_timeout = factory.Faker("boolean")
    custom_timeout = factory.Maybe(
        "has_custom_timeout",
        factory.Faker("random_int", min=0, max=600),
        None,
    )
    has_url_prefix = factory.Faker("boolean")
    url_prefix = factory.Maybe(
        "has_url_prefix",
        factory.Faker("url"),
        "",
    )
