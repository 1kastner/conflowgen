"""
Check if time ranges are working
"""

import datetime
import unittest

from conflowgen.domain_models.factories.fleet_factory import create_arrivals_within_time_range


class TestVehicleFactory__create_arrivals_within_time_range(unittest.TestCase):

    def test_create_time_range_happy_path(self) -> None:
        """This is the happy path"""
        arrivals = create_arrivals_within_time_range(
            datetime.date(2021, 7, 7),
            datetime.date(2021, 7, 9),
            datetime.date(2021, 7, 18),
            7,
            datetime.time(15, 0)
        )
        self.assertEqual(len(arrivals), 2)
        self.assertEqual(arrivals[0], datetime.datetime(2021, 7, 9, 15))
        self.assertEqual(arrivals[1], datetime.datetime(2021, 7, 16, 15))

    def test_create_time_range_fixed_vehicle_arrival_before_range(self) -> None:
        """The one fixed date a vehicle arrives lies before the time range"""
        arrivals = create_arrivals_within_time_range(
            datetime.date(2021, 7, 7),
            datetime.date(2021, 7, 2),
            datetime.date(2021, 7, 18),
            7,
            datetime.time(15, 0)
        )
        self.assertEqual(len(arrivals), 2)
        self.assertEqual(arrivals[0], datetime.datetime(2021, 7, 9, 15))
        self.assertEqual(arrivals[1], datetime.datetime(2021, 7, 16, 15))

    def test_create_time_range_fixed_vehicle_arrival_after_range(self) -> None:
        """The one fixed date a vehicle arrives lies after the time range"""
        arrivals = create_arrivals_within_time_range(
            datetime.date(2021, 7, 7),
            datetime.date(2021, 7, 30),
            datetime.date(2021, 7, 18),
            7,
            datetime.time(15, 0)
        )
        self.assertEqual(len(arrivals), 2)
        self.assertEqual(arrivals[0], datetime.datetime(2021, 7, 9, 15))
        self.assertEqual(arrivals[1], datetime.datetime(2021, 7, 16, 15))

    def test_create_time_range_with_ten_day_interval(self) -> None:
        """The one fixed date a vehicle arrives lies after the time range"""
        arrivals = create_arrivals_within_time_range(
            datetime.date(2021, 7, 7),
            datetime.date(2021, 7, 8),
            datetime.date(2021, 7, 18),
            10,
            datetime.time(15, 0)
        )
        self.assertEqual(len(arrivals), 2)
        self.assertEqual(arrivals[0], datetime.datetime(2021, 7, 8, 15))
        self.assertEqual(arrivals[1], datetime.datetime(2021, 7, 18, 15))

    def test_create_time_range_with_five_day_interval(self) -> None:
        """The one fixed date a vehicle arrives lies after the time range"""
        arrivals = create_arrivals_within_time_range(
            datetime.date(2021, 7, 7),
            datetime.date(2021, 7, 8),
            datetime.date(2021, 7, 18),
            5,
            datetime.time(15, 0)
        )
        self.assertEqual(len(arrivals), 3)
        self.assertEqual(arrivals[0], datetime.datetime(2021, 7, 8, 15))
        self.assertEqual(arrivals[1], datetime.datetime(2021, 7, 13, 15))
        self.assertEqual(arrivals[2], datetime.datetime(2021, 7, 18, 15))

    def test_create_time_range_with_single_vehicle(self) -> None:
        arrivals = create_arrivals_within_time_range(
            datetime.date(2021, 7, 7),
            datetime.date(2021, 7, 8),
            datetime.date(2021, 7, 18),
            -1,
            datetime.time(15, 0)
        )
        self.assertEqual(len(arrivals), 1)
        self.assertEqual(arrivals[0], datetime.datetime(2021, 7, 8, 15))

    def test_create_time_range_with_single_vehicle_out_of_time_range(self) -> None:
        arrivals = create_arrivals_within_time_range(
            datetime.date(2021, 7, 7),
            datetime.date(2021, 7, 23),
            datetime.date(2021, 7, 18),
            -1,
            datetime.time(15, 0)
        )
        self.assertEqual(len(arrivals), 0)
