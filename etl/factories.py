import factory

from etl import models


class ImportRecordFactory(factory.django.DjangoModelFactory):
    old_id = factory.Faker("random_int")
    old_table_name = factory.Faker("word")
    new_id = factory.Faker("random_int")
    new_table_name = factory.Faker("word")
    source_record = factory.Dict(
        {
            "old_slug": factory.Faker("word"),
        }
    )

    class Meta:
        model = models.ImportRecord
