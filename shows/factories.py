import datetime
import factory
import factory.fuzzy
import markdown
import string

from django.utils import text, timezone
from mdgen import MarkdownPostProvider

from . import models

factory.Faker.add_provider(MarkdownPostProvider)


class ShowFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Show
    title = factory.Faker('sentence')
    slug = factory.LazyAttribute(lambda o: text.slugify(o.title)[:255])
    logo = factory.django.ImageField()
    thumbnail = factory.django.ImageField()


class ContentFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = models.Content
        exclude = (
            'random_date_time',
            'raw_content',
        )

    class Params:
        draft = factory.Trait(
            published=False,
            pub_time=factory.fuzzy.FuzzyDateTime(
                start_dt=timezone.now(),
                end_dt=datetime.datetime(
                    2100, 1, 1, tzinfo=timezone.zoneinfo.ZoneInfo('UTC')
                )
            )
        )
        legacy_html = factory.Trait(
            content_format=models.Content.Format.HTML,
            original_content=factory.LazyAttribute(
                lambda o: markdown.markdown(o.raw_content)
            )
        )

    # Excluded
    random_date_time = factory.fuzzy.FuzzyDateTime(
        start_dt=datetime.datetime(
            2005, 1, 1, tzinfo=timezone.zoneinfo.ZoneInfo('UTC')
        )
    )
    raw_content = factory.Faker('post', size="medium")

    # Included
    title = factory.Faker('sentence')
    slug = factory.LazyAttribute(lambda o: text.slugify(o.title)[:255])
    image = factory.django.ImageField()
    show = factory.SubFactory(ShowFactory)
    catalog_number = factory.fuzzy.FuzzyText(
        length=8, chars=string.digits
    )
    published = True
    pub_time = factory.SelfAttribute('random_date_time')
    content_format = models.Content.Format.MARKDOWN
    original_content = factory.SelfAttribute('raw_content')
