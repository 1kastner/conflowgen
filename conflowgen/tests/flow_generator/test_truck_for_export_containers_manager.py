import datetime
import unittest
from collections import Counter

import matplotlib.pyplot as plt

from conflowgen import ModeOfTransport, StorageRequirement, ContainerLength
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_seeders import truck_arrival_distribution_seeder, \
    container_dwell_time_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck
from conflowgen.flow_generator.truck_for_export_containers_manager import \
    TruckForExportContainersManager
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckForExportContainersManager(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            TruckArrivalDistribution,
            ContainerDwellTimeDistribution,
            Container,
            Destination,
            Truck,
            LargeScheduledVehicle
        ])
        truck_arrival_distribution_seeder.seed()
        container_dwell_time_distribution_seeder.seed()

        # Enables visualisation, helpful for probability distributions
        # However, this blocks the execution of tests.
        self.debug = True

        self.manager = TruckForExportContainersManager()
        self.manager.reload_distribution()

    def visualize_probabilities(self, container: Container, drawn_times):
        import inspect  # pylint: disable=import-outside-toplevel
        import seaborn as sns  # pylint: disable=import-outside-toplevel
        container_dwell_time_distribution, truck_arrival_distribution = self.manager._get_distributions(container)
        sns.kdeplot(drawn_times, bw=0.01).set(title='Triggered from: ' + inspect.stack()[1].function)
        container_arrival_time = container.get_arrival_time()
        plt.axvline(x=container_arrival_time + container_dwell_time_distribution.minimum)
        plt.axvline(x=container_arrival_time + container_dwell_time_distribution.maximum)
        plt.show(block=True)

    def test_delivery_time_in_required_time_range_weekday(self):

        container_departure_time = datetime.datetime(
            year=2021, month=7, day=30, hour=11, minute=55
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )
        delivery_times = []
        for i in range(100):
            delivery_time = self.manager._get_container_delivery_time(container, container_departure_time)
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertTrue(delivery_time.weekday() != 6,
                            f"containers do not arrive on Sundays, but here we had {delivery_time} in round {i + 1}")
            delivery_times.append(delivery_time)

        if self.debug:
            self.visualize_probabilities(container, delivery_times)

    def test_delivery_time_in_required_time_range_with_sunday(self):
        container_departure_time = datetime.datetime(
            year=2021, month=8, day=2, hour=11, minute=30  # 11:30 -3h dwell time = 08:30 latest arrival
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )
        delivery_times = []
        for i in range(100):
            delivery_time = self.manager._get_container_delivery_time(container, container_departure_time)
            delivery_times.append(delivery_time)
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertTrue(delivery_time.weekday() != 6,
                            f"containers do not arrive on Sundays, but here we had {delivery_time} in round {i + 1}")

        if self.debug:
            self.visualize_probabilities(container, delivery_times)

        weekday_counter = Counter([delivery_time.weekday() for delivery_time in delivery_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday must be counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday must be counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday must be counted (02.08.2021)")

    def test_delivery_time_in_required_time_range_with_sunday_and_at_different_day_times(self):
        container_departure_time = datetime.datetime(
            year=2021, month=8, day=2, hour=11, minute=2
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )
        delivery_times = []
        for i in range(100):
            delivery_time = self.manager._get_container_delivery_time(container, container_departure_time)
            delivery_times.append(delivery_time)
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertNotEqual(delivery_time.weekday(), 6,
                                f"containers do not arrive on Sundays, "
                                f"but here we had {delivery_time} in round {i + 1}")

        if self.debug:
            self.visualize_probabilities(container, delivery_times)

        weekday_counter = Counter([delivery_time.weekday() for delivery_time in delivery_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday must be counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday must be counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday must be counted (02.08.2021)")
