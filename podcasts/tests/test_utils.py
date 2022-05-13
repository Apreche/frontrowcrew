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
