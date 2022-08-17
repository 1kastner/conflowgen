import datetime
import unittest

from conflowgen.analyses.abstract_analysis import get_hour_based_range


class TestHelpers(unittest.TestCase):
    def test_get_hour_based_range_normal(self):
        _range = get_hour_based_range(
            start=datetime.datetime(2022, 8, 15, 21),
            end=datetime.datetime(2022, 8, 16, 9),
            include_end=True
        )
        self.assertListEqual(
            [
                datetime.datetime(2022, 8, 15, 21),
                datetime.datetime(2022, 8, 15, 22),
                datetime.datetime(2022, 8, 15, 23),
                datetime.datetime(2022, 8, 16, 0),
                datetime.datetime(2022, 8, 16, 1),
                datetime.datetime(2022, 8, 16, 2),
                datetime.datetime(2022, 8, 16, 3),
                datetime.datetime(2022, 8, 16, 4),
                datetime.datetime(2022, 8, 16, 5),
                datetime.datetime(2022, 8, 16, 6),
                datetime.datetime(2022, 8, 16, 7),
                datetime.datetime(2022, 8, 16, 8),
                datetime.datetime(2022, 8, 16, 9),
            ],
            _range
        )

        _range = get_hour_based_range(
            start=datetime.datetime(2022, 8, 15, 21),
            end=datetime.datetime(2022, 8, 16, 9),
            include_end=False
        )
        self.assertListEqual(
            [
                datetime.datetime(2022, 8, 15, 21),
                datetime.datetime(2022, 8, 15, 22),
                datetime.datetime(2022, 8, 15, 23),
                datetime.datetime(2022, 8, 16, 0),
                datetime.datetime(2022, 8, 16, 1),
                datetime.datetime(2022, 8, 16, 2),
                datetime.datetime(2022, 8, 16, 3),
                datetime.datetime(2022, 8, 16, 4),
                datetime.datetime(2022, 8, 16, 5),
                datetime.datetime(2022, 8, 16, 6),
                datetime.datetime(2022, 8, 16, 7),
                datetime.datetime(2022, 8, 16, 8),
            ],
            _range
        )

    def test_get_hour_based_range_for_same_hour(self):
        _range = get_hour_based_range(
            start=datetime.datetime(2022, 8, 15, 21),
            end=datetime.datetime(2022, 8, 15, 21),
            include_end=True
        )
        self.assertListEqual(
            [
                datetime.datetime(2022, 8, 15, 21),
            ],
            _range
        )
        _range = get_hour_based_range(
            start=datetime.datetime(2022, 8, 15, 21),
            end=datetime.datetime(2022, 8, 15, 21),
            include_end=False
        )
        self.assertEqual(0, len(_range))
