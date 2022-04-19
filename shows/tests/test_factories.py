import inspect
import factory
from django.db import models as django_models
from django import test

from .. import factories, models


class FactoryExistenceTests(test.TestCase):
    def setUp(self):
        self.models = {
            model_name: model_class for model_name, model_class in inspect.getmembers(
                models, inspect.isclass
            ) if isinstance(model_class, django_models.Model) and not model_class._meta.abstract
        }
        self.factories = {
            factory_name: factory_class for factory_name, factory_class in inspect.getmembers(
                factories, inspect.isclass
            ) if isinstance(factory_class, factory.base.FactoryMetaClass) and not factory_class._meta.abstract
        }

    def test_factory_existence(self):
        factory_suffix = "Factory"
        for model_name, cls in self.models.items():
            factory_name = f"{model_name}{factory_suffix}"
            self.assertIn(factory_name, self.factories)
            self.assertEqual(cls, self.factories[factory_name]._meta.model)


class FactoryFunctionTestMeta(type):
    def __new__(cls, name, bases, attrs):
        factory_dict = {
            factory_name: factory_class for factory_name, factory_class in inspect.getmembers(
                factories, inspect.isclass
            ) if isinstance(factory_class, factory.base.FactoryMetaClass) and not factory_class._meta.abstract
        }
        for factory_name, factory_class in factory_dict.items():
            test_name = f"test_{factory_name}_create"
            attrs[test_name] = cls.gen_factory_test(factory_class)
        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def gen_factory_test(cls, factory):
        def fn(self):
            return self._run_factory_test(factory)
        return fn


class FactoryFunctionTest(test.TestCase, metaclass=FactoryFunctionTestMeta):
    def _run_factory_test(self, factory):
        obj = factory.create()
        self.assertTrue(isinstance(obj, factory._meta.model))
