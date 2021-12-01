import datetime
import unittest
from collections import Counter

import matplotlib.pyplot as plt
import seaborn as sns

from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_seeders import truck_arrival_distribution_seeder
from conflowgen.container_flow_data_generation_process.truck_for_import_containers_manager import \
    TruckForImportContainersManager
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckForImportContainersManager(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            TruckArrivalDistribution
        ])
        truck_arrival_distribution_seeder.seed()

        # Enables visualisation, helpful for probability distributions
        # However, this blocks the execution of tests.
        self.debug = False

    def test_pickup_time_in_required_time_range_weekday(self):
        manager = TruckForImportContainersManager()
        manager.reload_distribution(
            minimum_dwell_time_in_hours=3,
            maximum_dwell_time_in_hours=(5 * 24)
        )
        _datetime = datetime.datetime(
            year=2021, month=8, day=1
        )
        pickup_times = []
        for _ in range(1000):
            pickup_time = manager._get_container_pickup_time(_datetime)
            self.assertGreaterEqual(pickup_time, _datetime)
            self.assertLessEqual(pickup_time.date(), datetime.date(
                year=2021, month=8, day=6
            ))
            pickup_times.append(pickup_time)

        if self.debug:
            sns.kdeplot(pickup_times, bw=0.01)
            plt.show(block=True)

    def test_pickup_time_in_required_time_range_with_sunday_starting_from_a_full_hour(self):
        manager = TruckForImportContainersManager()
        manager.reload_distribution(
            minimum_dwell_time_in_hours=3,
            maximum_dwell_time_in_hours=(5 * 24)
        )
        _datetime = datetime.datetime(
            year=2021, month=8, day=6  # a Monday
        )
        pickup_times = []
        for _ in range(1000):
            pickup_time = manager._get_container_pickup_time(_datetime)
            pickup_times.append(pickup_time)
            self.assertGreaterEqual(pickup_time, _datetime)
            self.assertLessEqual(pickup_time.date(), datetime.date(
                year=2021, month=8, day=11
            ))
            self.assertTrue(pickup_time.weekday() != 6,
                            f"containers are not picked up on Sundays but {pickup_time} was presented")

        weekday_counter = Counter([pickup_time.weekday() for pickup_time in pickup_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday was counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday was counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday was counted (02.08.2021)")
        if self.debug:
            sns.kdeplot(pickup_times, bw=0.01)
            plt.show(block=True)

    def test_pickup_time_in_required_time_range_with_sunday_starting_within_an_hour(self):
        manager = TruckForImportContainersManager()
        manager.reload_distribution(
            minimum_dwell_time_in_hours=3,
            maximum_dwell_time_in_hours=(5 * 24)
        )
        _datetime = datetime.datetime(
            year=2021, month=8, day=6, hour=12, minute=13  # a Monday
        )
        pickup_times = []
        for _ in range(1000):
            pickup_time = manager._get_container_pickup_time(_datetime)
            pickup_times.append(pickup_time)
            self.assertGreaterEqual(pickup_time, _datetime)
            self.assertLessEqual(pickup_time.date(), datetime.date(
                year=2021, month=8, day=11
            ))
            self.assertTrue(pickup_time.weekday() != 6,
                            f"containers are not picked up on Sundays but {pickup_time} was presented")

        weekday_counter = Counter([pickup_time.weekday() for pickup_time in pickup_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday was counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday was counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday was counted (02.08.2021)")
        if self.debug:
            sns.kdeplot(pickup_times, bw=0.01)
            plt.show(block=True)
