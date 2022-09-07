import factory
import random

from . import models
from podcasts import models as podcast_models


class EpisodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Episode
        exclude = (
            "force_itunes_episode_number",
            "has_description",
            "has_author_name",
            "has_author_email",
            "has_image",
            "has_image_description",
            "has_itunes_title",
            "has_itunes_image",
            "has_itunes_image_description",
            "has_itunes_season_number",
            "has_itunes_episode_number",
            "has_itunes_episode_type",
            "has_itunes_block",
        )

    processed = factory.Faker("boolean")
    mp3 = factory.SubFactory("media.factories.MP3Factory")
    destination = factory.SubFactory("media.factories.FTPDestinationFactory")
    show = factory.SubFactory(
        "shows.factories.ShowFactory",
        is_podcast=True,
    )
    title = factory.Faker("sentence", nb_words=4)
    catalog_number = factory.Faker("numerify", text="########")
    pub_time = factory.Faker(
        "past_datetime",
        tzinfo=factory.Faker("pytimezone")
    )
    body = factory.Faker("post", size="medium")

    # optional
    has_description = factory.Faker("boolean")
    description = factory.Maybe(
        "has_description",
        factory.Faker("paragraph"),
        "",
    )
    has_author_name = factory.Faker("boolean")
    author_name = factory.Maybe(
        "has_author_name",
        factory.Faker("name"),
        "",
    )
    has_author_email = factory.Faker("boolean")
    author_email = factory.Maybe(
        "has_author_email",
        factory.Faker("email"),
        "",
    )
    has_image = factory.Faker("boolean")
    image = factory.Maybe(
        "has_image",
        factory.django.ImageField(width=3000, height=3000),
        "",
    )
    has_image_description = factory.Faker("boolean")
    image_description = factory.Maybe(
        "has_image_description",
        factory.Faker("sentence"),
        "",
    )
    has_itunes_image = factory.Faker("boolean")
    itunes_image = factory.Maybe(
        "has_itunes_image",
        factory.django.ImageField(width=3000, height=3000),
        "",
    )
    has_itunes_image_description = factory.Faker("boolean")
    itunes_image_description = factory.Maybe(
        "has_image_description",
        factory.Faker("sentence"),
        "",
    )
    has_itunes_title = factory.Faker("boolean")
    itunes_title = factory.Maybe(
        "has_itunes_title",
        factory.Faker("sentence"),
        "",
    )
    force_itunes_episode_number = factory.Faker("boolean")
    has_itunes_episode_number = factory.LazyAttribute(
        lambda o: o.force_itunes_episode_number or (
            o.show.podcast.itunes_type == podcast_models.Podcast.PodcastType.SERIAL
        )
    )
    itunes_episode_number = factory.Maybe(
        "has_itunes_episode_number",
        factory.Sequence(lambda n: n),
        None,
    )
    has_itunes_season_number = factory.Faker("boolean")
    itunes_season_number = factory.Maybe(
        "has_itunes_season_number",
        factory.Faker(
            "random_int", min=0, max=3,
        ),
        None,
    )
    itunes_explicit = factory.Faker("null_boolean")
    itunes_episode_type = factory.Faker(
        "random_element",
        elements=podcast_models.PodcastEpisode.EpisodeType,
    )
    itunes_block = factory.Faker("boolean", chance_of_getting_true=1)

    related_links = factory.RelatedFactoryList(
        "creator.factories.RelatedLinkFactory",
        factory_related_name="episode",
        size=lambda: random.randint(0, 4),
    )

    chapters = factory.RelatedFactoryList(
        "creator.factories.ChapterFactory",
        factory_related_name="episode",
        size=lambda: random.randint(0, 7),
    )

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if create and extracted:
            for tag in extracted:
                self.tags.add(tag)


class RelatedLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RelatedLink
        exclude = (
            "has_description",
        )

    episode = factory.SubFactory("creator.factories.EpisodeFactory")
    title = factory.Faker("sentence", nb_words=4)
    url = factory.Faker("uri")
    author = factory.Faker("name")
    has_description = factory.Faker("boolean")
    description = factory.Maybe(
        "has_description",
        factory.Faker("paragraph"),
        "",
    )


class ChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Chapter
        exclude = (
            "has_description",
            "has_end_time",
            "has_image",
            "has_image_description",
            "has_url",
            "has_url_description",
        )

    episode = factory.SubFactory("creator.factories.EpisodeFactory")
    start_time = factory.Faker("random_int", max=3600000)
    end_time = factory.Maybe(
        "has_end_time",
        factory.Faker(
            "random_int",
            min=factory.SelfAttribute("..start_time"),
        ),
        None,
    )
    title = factory.Faker("sentence", nb_words=4)
    has_description = factory.Faker("boolean")
    description = factory.Maybe(
        "has_description",
        factory.Faker("paragraph"),
        "",
    )
    has_url = factory.Faker("boolean")
    url = factory.Faker("uri")
    has_url_description = factory.Faker("boolean")
    url_description = factory.Maybe(
        "has_url_description",
        factory.Faker("paragraph"),
        "",
    )
    has_image = factory.Faker("boolean")
    image = factory.Maybe(
        "has_image",
        factory.django.ImageField(width=3000, height=3000),
        "",
    )
    has_image_description = factory.Faker("boolean")
    image_description = factory.Maybe(
        "has_image_description",
        factory.Faker("sentence"),
        "",
    )
