import datetime
import unittest

from conflowgen.tools.weekly_distribution import WeeklyDistribution


class TestWeeklyDistribution(unittest.TestCase):

    def test_simple_slice(self):
        weekly_distribution = WeeklyDistribution([
            (0, .5),
            (24, .2),
            (48, .2),
            (72, .1),
            (96, 0),
            (120, 0),
            (144, 0)
        ],
            considered_time_window_in_hours=48
        )
        _datetime = datetime.datetime(
            year=2021, month=8, day=2, hour=3
        )
        self.assertEqual(_datetime.weekday(), 0)  # assert is Monday
        distribution_slice = weekly_distribution.get_distribution_slice(_datetime)
        self.assertEqual(len(distribution_slice), 2)
        self.assertListEqual(list(distribution_slice.keys()), [21, 45])
        self.assertAlmostEqual(sum(list(distribution_slice.values())), 1)

    def test_simple_with_long_minimum_dwell_time(self):
        weekly_distribution = WeeklyDistribution([
            (0, .5),
            (24, .2),
            (48, .2),
            (72, .1),
            (96, 0),
            (120, 0),
            (144, 0)
        ],
            considered_time_window_in_hours=36
        )
        _datetime = datetime.datetime(
            year=2021, month=8, day=2
        )
        self.assertEqual(_datetime.weekday(), 0)  # assert is Monday
        distribution_slice = weekly_distribution.get_distribution_slice(_datetime)
        self.assertDictEqual(
            distribution_slice, {
                0: 0.7142857142857143,
                24: 0.28571428571428575
            }
        )

    def test_slice_into_next_two_weeks(self):
        weekly_distribution = WeeklyDistribution([
            (0, .5),
            (24, .2),
            (48, .2),
            (72, .1),
            (96, 0),
            (120, 0),
            (144, 0)
        ],
            considered_time_window_in_hours=(7 * 24)
        )
        _datetime = datetime.datetime(
            year=2021, month=8, day=1, hour=0
        )
        self.assertEqual(_datetime.weekday(), 6)  # assert is Sunday
        distribution_slice = weekly_distribution.get_distribution_slice(_datetime)
        assumed_slice = {
            0: 0,
            24: .5,
            48: .2,
            72: .2,
            96: .1,
            120: 0,
            144: 0
        }
        self.assertEqual(assumed_slice.keys(), distribution_slice.keys())
        for key in distribution_slice.keys():
            self.assertAlmostEqual(
                assumed_slice[key],
                distribution_slice[key],
                msg=f"Difference for key={key}: "
                    f"assumed: {assumed_slice[key]}, "
                    f"is: {distribution_slice[key]}"
            )

    # noinspection PyUnusedLocal
    def test_sunday_is_missing_for_delivery(self):
        distribution_monday_to_saturday = [
            1 / (24 * 6)
            for hour in range(24)
            for day in range(6)  # Monday to Saturday
        ]
        distribution_sunday = [0 for hour in range(24)]
        # noinspection PyTypeChecker
        distribution = dict(list(enumerate(distribution_monday_to_saturday + distribution_sunday)))

        weekly_distribution = WeeklyDistribution(
            list(distribution.items()),
            considered_time_window_in_hours=72,  # 3 days before delivery is allowed
        )
        container_departure_time = datetime.datetime(
            year=2021, month=8, day=2, hour=11, minute=30
        )
        self.assertEqual(container_departure_time.weekday(), 0)  # assert is Monday

        latest_slot = container_departure_time.replace(minute=0, second=0, microsecond=0)
        earliest_slot = latest_slot - datetime.timedelta(hours=71)
        distribution_slice = weekly_distribution.get_distribution_slice(earliest_slot)
        hours = list(distribution_slice.keys())
        self.assertEqual(72, len(hours))
        self.assertAlmostEqual(sum(list(distribution_slice.values())), 1, places=1,
                               msg="Severe rounding issues exist.")
        visited_sunday = False
        visited_working_day = False
        for hour_of_the_week_since_earliest_arrival in hours:
            drawn_time = earliest_slot + datetime.timedelta(hours=hour_of_the_week_since_earliest_arrival)
            if drawn_time.weekday() == 6:
                visited_sunday = True
                self.assertEqual(distribution_slice[hour_of_the_week_since_earliest_arrival], 0,
                                 "Assert no arrivals on Sunday")
            else:
                visited_working_day = True
                self.assertGreater(distribution_slice[hour_of_the_week_since_earliest_arrival], 0,
                                   "Assert arrivals on other days")
        self.assertTrue(visited_sunday)
        self.assertTrue(visited_working_day)

    # noinspection PyUnusedLocal
    def test_correct_starting_and_end_hour_when_looking_forward(self):
        distribution_monday_to_saturday = [
            1 / (24 * 6)
            for hour in range(24)
            for day in range(6)  # Monday to Saturday
        ]
        distribution_sunday = [0 for hour in range(24)]
        # noinspection PyTypeChecker
        distribution = dict(list(enumerate(distribution_monday_to_saturday + distribution_sunday)))

        weekly_distribution = WeeklyDistribution(
            list(distribution.items()),
            considered_time_window_in_hours=72,  # 3 days before delivery is allowed
        )
        container_departure_time = datetime.datetime(
            year=2021, month=8, day=2, hour=11, minute=30
        )
        self.assertEqual(container_departure_time.weekday(), 0)  # assert is Monday

        earliest_slot_input = (
                container_departure_time.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        )
        latest_slot_input = earliest_slot_input + datetime.timedelta(hours=71)

        distribution_slice = weekly_distribution.get_distribution_slice(earliest_slot_input)
        time_slots = list(distribution_slice.keys())
        earliest_time_slot = min(time_slots)
        self.assertEqual(earliest_time_slot, 0)
        latest_time_slot = max(time_slots)
        self.assertEqual(latest_time_slot, 71)

    # noinspection PyUnusedLocal
    def test_correct_starting_and_end_hour_when_looking_backward(self):
        distribution_monday_to_saturday = [
            1 / (24 * 6)
            for hour in range(24)
            for day in range(6)  # Monday to Saturday
        ]
        distribution_sunday = [0 for hour in range(24)]
        # noinspection PyTypeChecker
        distribution = dict(list(enumerate(distribution_monday_to_saturday + distribution_sunday)))

        weekly_distribution = WeeklyDistribution(
            list(distribution.items()),
            considered_time_window_in_hours=72,  # 3 days before delivery is allowed
        )
        container_departure_time = datetime.datetime(
            year=2021, month=8, day=2, hour=11, minute=30
        )
        self.assertEqual(container_departure_time.weekday(), 0)  # assert is Monday

        earliest_slot_input = (
                container_departure_time.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=72)
        )

        distribution_slice = weekly_distribution.get_distribution_slice(earliest_slot_input)
        time_slots = list(distribution_slice.keys())
        earliest_time_slot = min(time_slots)
        self.assertEqual(earliest_time_slot, 0)
        latest_time_slot = max(time_slots)
        self.assertEqual(latest_time_slot, 71)

    def test_get_time_of_the_week_for_full_hour(self):
        hour_of_the_week = WeeklyDistribution._get_hour_of_the_week_from_datetime(datetime.datetime(2022, 8, 9, 11))
        self.assertEqual(hour_of_the_week, 35)

    def test_get_time_of_the_week_for_started_hour(self):
        hour_of_the_week = WeeklyDistribution._get_hour_of_the_week_from_datetime(datetime.datetime(2022, 8, 9, 11, 30))
        self.assertEqual(hour_of_the_week, 35)
