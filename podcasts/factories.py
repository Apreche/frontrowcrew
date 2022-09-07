import datetime
import factory
import random

from django.utils import timezone
from mdgen import MarkdownPostProvider

from . import models

factory.Faker.add_provider(MarkdownPostProvider)


class iTunesCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.iTunesCategory
        exclude = ("has_subcategory",)

    description = factory.Faker("sentence", nb_words=3)
    has_subcategory = factory.Faker("boolean")
    subcategory_description = factory.Maybe(
        "has_subcategory",
        factory.Faker("sentence", nb_words=3),
        "",
    )


class iTunesOwnerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.iTunesOwner

    name = factory.Faker("name")
    email = factory.Faker("email")


class PodcastFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Podcast
        exclude = (
            "set_explicit",
            "has_copyright",
            "has_creative_commons_license",
            "has_custom_public_feed_url",
            "has_itunes_owner",
            "has_itunes_title",
            "has_image",
            "has_image_description",
            "has_managing_editor",
            "has_secondary_category",
            "has_ttl",
            "has_web_master",
        )

    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")
    # TODO: Podcast RSS supports only ISO 639-1 which is 2-character codes
    # This faker returns 3-character codes, so it breaks
    # language = factory.Faker("language_code")
    language = factory.Faker(
        "random_element", elements=["en", "fr", "es"]
    )
    has_managing_editor = factory.Faker("boolean")
    managing_editor = factory.Maybe(
        "has_managing_editor",
        factory.Faker("email"),
        "",
    )
    has_web_master = factory.Faker("boolean")
    web_master = factory.Maybe(
        "has_web_master",
        factory.Faker("email"),
        "",
    )
    has_ttl = factory.Faker("boolean")
    ttl = factory.Maybe(
        "has_ttl",
        factory.Faker("random_int", min=0, max=120),
        None,
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

    itunes_image = factory.django.ImageField(width=3000, height=3000)
    itunes_primary_category = factory.Iterator(
        models.iTunesCategory.objects.all()
    )
    has_secondary_category = factory.Faker("boolean")
    itunes_secondary_category = factory.Maybe(
        "has_secondary_category",
        factory.Iterator(
            models.iTunesCategory.objects.all()
        ),
        None,
    )
    itunes_explicit = factory.Faker("null_boolean")
    itunes_author = factory.Faker("name")
    has_itunes_owner = factory.Faker("boolean")
    itunes_owner = factory.Maybe(
        "has_itunes_owner",
        factory.SubFactory(iTunesOwnerFactory),
        None,
    )
    has_itunes_title = factory.Faker("boolean")
    itunes_title = factory.Maybe(
        "has_itunes_title",
        factory.Faker("sentence"),
        "",
    )
    itunes_type = factory.Faker(
        "random_element", elements=models.Podcast.PodcastType
    )
    itunes_block = factory.Faker("boolean", chance_of_getting_true=1)
    itunes_complete = factory.Faker("boolean", chance_of_getting_true=1)
    has_copyright = factory.Faker("boolean")
    copyright = factory.Maybe(
        "has_copyright",
        factory.Faker("sentence"),
        "",
    )
    has_creative_commons_license = factory.Faker("boolean")
    creative_commons_license = factory.Maybe(
        "has_creative_commons_license",
        factory.Faker("url"),
        "",
    )
    chapters = factory.RelatedFactoryList(
        "podcasts.factories.PodcastEpisodeFactory",
        factory_related_name="podcast",
        size=lambda: random.randint(0, 10)
    )

    has_custom_public_feed_url = factory.Faker("boolean")
    custom_public_feed_url = factory.Maybe(
        "has_custom_public_feed_url",
        factory.Faker("url"),
        "",
    )


class PodcastEnclosureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PodcastEnclosure

    url = factory.Faker("uri")
    length = factory.Faker("random_int", min=1, max=1000000000)
    type = factory.Faker(
        "random_element", elements=models.PodcastEnclosure.EnclosureType
    )


class PodcastChapterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PodcastChapter
        exclude = (
            "has_description",
            "has_end_time",
            "has_url",
            "has_url_description",
            "has_image",
            "has_image_description",
        )

    episode = factory.SubFactory(
        "podcasts.factories.PodcastEpisodeFactory"
    )
    start_time = factory.Faker("random_int", min=0, max=100000)
    has_end_time = factory.Faker("boolean")
    end_time = factory.Maybe(
        "has_end_time",
        factory.Faker(
            "randomize_nb_elements",
            number=factory.SelfAttribute("..start_time"),
            ge=True,
        ),
        None,
    )
    title = factory.Faker("text", max_nb_chars=255)
    has_description = factory.Faker("boolean")
    description = factory.Maybe(
        "has_description",
        factory.Faker("words"),
        "",
    )
    has_url = factory.Faker("boolean")
    url = factory.Maybe(
        "has_url",
        factory.Faker("url"),
        "",
    )
    has_url_description = factory.Faker("boolean")
    url_description = factory.Maybe(
        "has_url_description",
        factory.Faker("sentence"),
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


class PodcastEpisodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PodcastEpisode
        exclude = (
            "duration_in_seconds",
            "force_itunes_episode_number",
            "has_author_name",
            "has_author_email",
            "has_comments",
            "has_image",
            "has_image_description",
            "has_itunes_image",
            "has_itunes_title",
            "has_itunes_episode_number",
            "has_itunes_season_number",
        )

    podcast = factory.SubFactory(PodcastFactory)
    title = factory.Faker("sentence")
    enclosure = factory.SubFactory(PodcastEnclosureFactory)
    guid_is_permalink = factory.Faker("boolean")
    guid = factory.Maybe(
        "guid_is_permalink",
        factory.Faker("url"),
        factory.Faker("uuid4"),
    )
    pub_date = factory.Faker("date_time", tzinfo=timezone.utc)
    description = factory.Faker("paragraph")
    duration_in_seconds = factory.Faker(
        "random_int", min=1, max=7200
    )
    duration = factory.LazyAttribute(
        lambda o: datetime.timedelta(
            seconds=o.duration_in_seconds
        )
    )
    has_author_name = factory.Faker("boolean")
    author_name = factory.Maybe(
        "has_author_name",
        factory.Faker("name"),
        ""
    )
    has_author_email = factory.Faker("boolean")
    author_email = factory.Maybe(
        "has_author_email",
        factory.Faker("email"),
        "",
    )
    has_comments = factory.Faker("boolean")
    comments = factory.Maybe(
        "has_comments",
        factory.Faker("url"),
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
    itunes_explicit = factory.Faker("null_boolean")
    has_itunes_title = factory.Faker("boolean")
    itunes_title = factory.Maybe(
        "has_itunes_title",
        factory.Faker("sentence"),
        "",
    )

    force_itunes_episode_number = factory.Faker("boolean")
    has_itunes_episode_number = factory.LazyAttribute(
        lambda o: o.force_itunes_episode_number or (
            o.podcast.itunes_type == models.Podcast.PodcastType.SERIAL
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
    itunes_episode_type = factory.Faker(
        "random_element",
        elements=models.PodcastEpisode.EpisodeType,
    )
    itunes_block = factory.Faker("boolean", chance_of_getting_true=1)

    chapters = factory.RelatedFactoryList(
        "podcasts.factories.PodcastChapterFactory",
        factory_related_name="episode",
        size=lambda: random.randint(0, 5)
    )
