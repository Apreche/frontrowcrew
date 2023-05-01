import random

import factory
import markdown
from django.utils import text
from mdgen import MarkdownPostProvider

from . import models

factory.Faker.add_provider(MarkdownPostProvider)


class PublishableFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Publishable
        abstract = True

    is_published = factory.Faker("boolean")
    pub_time = factory.Maybe(
        "is_published",
        factory.Faker("past_datetime", tzinfo=factory.Faker("pytimezone")),
        factory.Faker("future_datetime", tzinfo=factory.Faker("pytimezone")),
    )


class ShowFactory(PublishableFactory):
    class Meta:
        model = models.Show
        exclude = (
            "has_description",
            "has_logo",
            "has_thumbnail",
            "is_podcast",
        )

    title = factory.Faker("sentence", nb_words=4)
    slug = factory.LazyAttribute(lambda o: text.slugify(o.title)[:255])
    has_description = factory.Faker("boolean")
    description = factory.Maybe(
        "has_description",
        factory.Faker("paragraph"),
        "",
    )
    has_logo = factory.Faker("boolean")
    logo = factory.Maybe(
        "has_image",
        factory.django.ImageField(width=3000, height=3000),
        "",
    )
    has_thumbnail = factory.Faker("boolean")
    thumbnail = factory.Maybe(
        "has_thumbnail",
        factory.django.ImageField(width=3000, height=3000),
        "",
    )
    display_in_nav = factory.Faker("boolean")

    is_podcast = factory.Faker("boolean")
    podcast = factory.Maybe(
        "is_podcast",
        factory.SubFactory("podcasts.factories.PodcastFactory"),
        None,
    )


class ContentFactory(PublishableFactory):
    class Meta:
        model = models.Content
        exclude = (
            "has_image",
            "has_image_description",
            "is_markdown",
            "is_podcast",
            "raw_content",
        )

    class Params:
        parent_is_podcast = factory.LazyAttribute(lambda o: o.show.podcast is not None)
        podcast = factory.Trait(
            is_podcast=True,
            show=factory.SubFactory(
                ShowFactory,
                is_podcast=True,
            ),
        )

    title = factory.Faker("sentence", nb_words=4)
    is_podcast = factory.Maybe(
        "parent_is_podcast",
        factory.Faker("boolean"),
        False,
    )
    show = factory.SubFactory(
        ShowFactory,
    )
    slug = factory.LazyAttribute(lambda o: text.slugify(o.title)[:255])
    catalog_number = factory.Faker("numerify", text="########")
    is_markdown = factory.Faker("boolean")
    raw_content = factory.Faker("post", size="medium")
    content_format = factory.Maybe(
        "is_markdown",
        models.Content.Format.MARKDOWN,
        models.Content.Format.HTML,
    )
    original_content = factory.Maybe(
        "is_markdown",
        factory.SelfAttribute("raw_content"),
        factory.LazyAttribute(lambda o: markdown.markdown(o.raw_content)),
    )
    podcast_episode = factory.Maybe(
        "is_podcast",
        factory.SubFactory(
            "podcasts.factories.PodcastEpisodeFactory",
            podcast=factory.SelfAttribute("..show.podcast"),
        ),
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

    related_links = factory.RelatedFactoryList(
        "shows.factories.RelatedLinkFactory",
        factory_related_name="content",
        size=lambda: random.randint(0, 4),
    )

    meta_data = factory.RelatedFactoryList(
        "shows.factories.MetaDataFactory",
        factory_related_name="content",
        size=lambda: random.randint(0, 4),
    )

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if create and extracted:
            for tag in extracted:
                self.tags.add(tag)


class RelatedLinkTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RelatedLinkType

    description = factory.Faker("word")

    @factory.lazy_attribute
    def plural_description(self):
        return f"{self.description}s"

    @factory.lazy_attribute
    def slug(self):
        return text.slugify(self.description)[:50]

    @factory.lazy_attribute
    def plural_slug(self):
        slug = text.slugify(self.description)[:49]
        return f"{slug}s"


class RelatedLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RelatedLink
        exclude = ("has_description",)

    class Params:
        # Never set published and unpublished together
        # Will be able to implement this properly when this issue is resolved
        # https://github.com/FactoryBoy/factory_boy/issues/435

        published = factory.Trait(
            content=factory.SubFactory(
                ContentFactory,
                is_published=True,
                show__is_published=True,
                related_links=[],
            )
        )
        unpublished = factory.Trait(
            content=factory.SubFactory(
                ContentFactory,
                is_published=False,
                related_links=[],
            )
        )
        use_new_type = factory.Trait(type=factory.SubFactory(RelatedLinkTypeFactory))

    content = factory.SubFactory(ContentFactory, related_links=[])
    type = factory.Iterator(models.RelatedLinkType.objects.all())
    title = factory.Faker("sentence", nb_words=4)
    has_description = factory.Faker("boolean")
    description = factory.Maybe(
        "has_description",
        factory.Faker("sentence", nb_words=10),
        "",
    )
    url = factory.Faker("uri")
    author = factory.Faker("first_name")
    error = factory.Faker("boolean")


class MetaDataTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MetaDataType

    description = factory.Faker("word")

    @factory.lazy_attribute
    def plural_description(self):
        return f"{self.description}s"

    @factory.lazy_attribute
    def slug(self):
        return text.slugify(self.description)[:50]

    @factory.lazy_attribute
    def plural_slug(self):
        slug = text.slugify(self.description)[:49]
        return f"{slug}s"


class MetaDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MetaData

    class Params:
        use_new_type = factory.Trait(type=factory.SubFactory(MetaDataTypeFactory))

    content = factory.SubFactory(ContentFactory, meta_data=[])
    type = factory.Iterator(models.MetaDataType.objects.all())
    data = factory.Faker("word")
