import logging

from django import test
from django.core.cache import cache


class FRCTestCase(test.TestCase):
    def setUp(self):
        logger = logging.getLogger("django.request")
        self.previous_level = logger.getEffectiveLevel()
        logger.setLevel(logging.ERROR)

    def tearDown(self):
        logger = logging.getLogger("django.request")
        logger.setLevel(self.previous_level)
        cache.clear()
