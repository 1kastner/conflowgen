import datetime
import unittest
from collections import Counter

import matplotlib.pyplot as plt
import seaborn as sns

from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_seeders import truck_arrival_distribution_seeder
from conflowgen.container_flow_data_generation_process.truck_for_export_containers_manager import \
    TruckForExportContainersManager
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckForExportContainersManager(unittest.TestCase):

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

        self.manager = TruckForExportContainersManager()
        self.manager.reload_distribution(
            minimum_dwell_time_in_hours=3,  # after ship arrival, at least 3h pass
            maximum_dwell_time_in_hours=(3 * 24)  # 3 days after ship arrival the container must have left the yard
        )

    def test_delivery_time_in_required_time_range_weekday(self):

        container_departure_time = datetime.datetime(
            year=2021, month=7, day=30, hour=11, minute=55
        )
        earliest_container_delivery = datetime.datetime(
            year=2021, month=7, day=27, hour=11, minute=55
        )
        delivery_times = []
        for i in range(1000):
            delivery_time = self.manager._get_container_delivery_time(container_departure_time)
            self.assertGreaterEqual(delivery_time, earliest_container_delivery,
                                    "container must not arrive earlier than three days before export, "
                                    f"but here we had {delivery_time} in round {i + 1}")
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertTrue(delivery_time.weekday() != 6,
                            f"containers do not arrive on Sundays, but here we had {delivery_time} in round {i + 1}")
            delivery_times.append(delivery_time)

        if self.debug:
            sns.kdeplot(delivery_times, bw=0.01)
            plt.show(block=True)

    def test_delivery_time_in_required_time_range_with_sunday(self):
        container_departure_time = datetime.datetime(
            year=2021, month=8, day=2, hour=11, minute=30  # 11:30 -3h dwell time = 08:30 latest arrival
        )
        earliest_container_delivery = datetime.datetime(
            year=2021, month=7, day=30, hour=11, minute=30
        )
        delivery_times = []
        for i in range(1000):
            delivery_time = self.manager._get_container_delivery_time(container_departure_time)
            delivery_times.append(delivery_time)
            self.assertGreaterEqual(delivery_time, earliest_container_delivery,
                                    "container must not arrive earlier than three days before export, "
                                    f"but here we had {delivery_time} in round {i + 1}")
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertTrue(delivery_time.weekday() != 6,
                            f"containers do not arrive on Sundays, but here we had {delivery_time} in round {i + 1}")

        weekday_counter = Counter([delivery_time.weekday() for delivery_time in delivery_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday must be counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday must be counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday must be counted (02.08.2021)")

        if self.debug:
            sns.kdeplot(delivery_times, bw=0.01)
            plt.show(block=True)

    def test_delivery_time_in_required_time_range_with_sunday_and_at_different_day_times(self):
        container_departure_time = datetime.datetime(
            year=2021, month=8, day=2, hour=11, minute=2
        )
        earliest_container_delivery = datetime.datetime(
            year=2021, month=7, day=30, hour=5, minute=0
        )
        delivery_times = []
        for i in range(1000):
            delivery_time = self.manager._get_container_delivery_time(container_departure_time)
            delivery_times.append(delivery_time)
            self.assertGreaterEqual(delivery_time, earliest_container_delivery,
                                    "container must not arrive earlier than three days before export, "
                                    f"but here we had {delivery_time} in round {i + 1}")
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertNotEqual(delivery_time.weekday(), 6,
                                f"containers do not arrive on Sundays, "
                                f"but here we had {delivery_time} in round {i + 1}")

        weekday_counter = Counter([delivery_time.weekday() for delivery_time in delivery_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday must be counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday must be counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday must be counted (02.08.2021)")

        if self.debug:
            sns.kdeplot(delivery_times, bw=0.01)
            plt.show(block=True)
