from django.test import TestCase

from .. import utils


class PodcastsUtilsTests(TestCase):

    def test_seconds_to_timespan(self):
        test_values = [
            (5, "05"),
            (37, "37"),
            (61, "01:01"),
            (468, "07:48"),
            (3540, "59:00"),
            (5752, "1:35:52"),
            (48430, "13:27:10"),
            (360000, "100:00:00"),
        ]
        for seconds, npt in test_values:
            self.assertEqual(
                utils.seconds_to_timespan(seconds),
                npt
            )

    def test_milliseconds_to_timespan(self):
        test_values = [
            (3499, "03"),
            (3501, "04"),
            (5000, "05"),
            (37000, "37"),
            (61000, "01:01"),
            (468000, "07:48"),
            (3540000, "59:00"),
            (5752000, "1:35:52"),
            (48430000, "13:27:10"),
            (48430900, "13:27:11"),
            (360000000, "100:00:00"),
        ]
        for milliseconds, npt in test_values:
            self.assertEqual(
                utils.milliseconds_to_timespan(milliseconds),
                npt
            )
