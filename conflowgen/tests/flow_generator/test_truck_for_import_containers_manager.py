from __future__ import annotations

import datetime
import math
import unittest
from collections import Counter

import matplotlib.pyplot as plt

from conflowgen import ModeOfTransport, StorageRequirement, ContainerLength
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from conflowgen.domain_models.distribution_seeders import truck_arrival_distribution_seeder, \
    container_dwell_time_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck
from conflowgen.flow_generator.truck_for_import_containers_manager import \
    TruckForImportContainersManager
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db
from conflowgen.tools.continuous_distribution import ContinuousDistribution
from conflowgen.tools.weekly_distribution import WeeklyDistribution


class TestTruckForImportContainersManager(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            TruckArrivalDistribution,
            ContainerDwellTimeDistribution,
            Container,
            Truck,
            LargeScheduledVehicle,
            Destination
        ])
        truck_arrival_distribution_seeder.seed()
        container_dwell_time_distribution_seeder.seed()

        container_dwell_time_distributions = ContainerDwellTimeDistributionRepository.get_distributions()
        self.container_dwell_time_distributions_from_x_to_truck = {
            vehicle_type: container_dwell_time_distributions[vehicle_type][ModeOfTransport.truck]
            for vehicle_type in ModeOfTransport
        }

        self.manager = TruckForImportContainersManager()
        self.manager.reload_distributions()

        # Enables visualisation, helpful for visualizing the probability distributions.
        # However, this blocks the execution of tests.
        self.visual_debug = False

    def visualize_probabilities(self, container, drawn_times, container_arrival_time):
        import inspect  # pylint: disable=import-outside-toplevel
        import seaborn as sns  # pylint: disable=import-outside-toplevel
        container_dwell_time_distribution, _ = self._get_distribution(container)
        sns.kdeplot(drawn_times, bw=0.01).set(title='Triggered from: ' + inspect.stack()[1].function)
        plt.axvline(x=container_arrival_time + datetime.timedelta(hours=container_dwell_time_distribution.minimum))
        plt.axvline(x=container_arrival_time + datetime.timedelta(hours=container_dwell_time_distribution.maximum))
        plt.show(block=True)

    def _get_distribution(self, container: Container) -> tuple[ContinuousDistribution, WeeklyDistribution | None]:

        # pylint: disable=protected-access
        container_dwell_time_distribution,  truck_arrival_distribution = self.manager._get_distributions(
            container)

        return container_dwell_time_distribution, truck_arrival_distribution

    def test_container_dwell_time_and_truck_arrival_distributions_match(self):
        container = Container.create(
            weight=20,
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard
        )
        container_dwell_time_distribution, truck_arrival_distribution = self._get_distribution(container)

        self.assertEqual(3, int(container_dwell_time_distribution.minimum))
        self.assertEqual(3, int(truck_arrival_distribution.minimum_dwell_time_in_hours))

        self.assertEqual(216, container_dwell_time_distribution.maximum)

        possible_hours_for_truck_arrival = truck_arrival_distribution.considered_time_window_in_hours
        self.assertEqual(
            216 - 3 - 1,
            possible_hours_for_truck_arrival,
            "The truck might arrive 216h after the arrival of the container, but not within the first three hours. "
            "Furthermore, the last hour is subtracted because up to 59 minutes are later added again and the maximum "
            "should not be surpassed."
        )

    def test_not_reversed_distribution_is_used(self):
        container = Container.create(
            weight=20,
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard
        )
        container_dwell_time_distribution, _ = self._get_distribution(container)
        self.assertFalse(container_dwell_time_distribution.reversed_distribution)

    def test_pickup_time_in_required_time_range_weekday(self):

        container_arrival_time = datetime.datetime(
            year=2021, month=8, day=1
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )
        pickup_times = []
        for _ in range(1000):
            pickup_time = self.get_pickup_time(container, container_arrival_time)
            self.assertGreaterEqual(pickup_time, container_arrival_time)
            pickup_times.append(pickup_time)

        if self.visual_debug:
            self.visualize_probabilities(container, pickup_times, container_arrival_time)

    def test_pickup_time_in_required_time_range_with_sunday_starting_from_a_full_hour(self):
        container_arrival_time = datetime.datetime(
            year=2021, month=8, day=6  # a Monday
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )
        pickup_times = []
        for _ in range(1000):
            pickup_time = self.get_pickup_time(container, container_arrival_time)
            pickup_times.append(pickup_time)
            self.assertGreaterEqual(pickup_time, container_arrival_time,
                                    "Container is picked up after it has arrived in the yard")
            self.assertTrue(pickup_time.weekday() != 6,
                            f"containers are not picked up on Sundays but {pickup_time} was presented")

        if self.visual_debug:
            self.visualize_probabilities(container, pickup_times, container_arrival_time)

        weekday_counter = Counter([pickup_time.weekday() for pickup_time in pickup_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday was counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday was counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday was counted (02.08.2021)")

    def get_pickup_time(self, container, container_arrival_time):

        # pylint: disable=protected-access
        pickup_time = self.manager._get_container_pickup_time(
            container, container_arrival_time
        )

        return pickup_time

    def test_pickup_time_in_required_time_range_with_sunday_starting_within_an_hour(self):
        container_arrival_time = datetime.datetime(
            year=2021, month=8, day=6, hour=12, minute=13  # a Monday
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )
        pickup_times = []
        for _ in range(1000):
            pickup_time = self.get_pickup_time(container, container_arrival_time)
            pickup_times.append(pickup_time)
            self.assertGreaterEqual(pickup_time, container_arrival_time,
                                    "Container is picked up after it has arrived in the yard")
            self.assertTrue(pickup_time.weekday() != 6,
                            f"containers are not picked up on Sundays but {pickup_time} was presented")

        if self.visual_debug:
            self.visualize_probabilities(container, pickup_times, container_arrival_time)

        weekday_counter = Counter([pickup_time.weekday() for pickup_time in pickup_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday was counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday was counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday was counted (02.08.2021)")

    def test_distributions_match(self):
        truck_arrival_distribution = self.manager.truck_arrival_distributions[ModeOfTransport.feeder][
            StorageRequirement.standard]
        dwell_time_distribution = self.container_dwell_time_distributions_from_x_to_truck[ModeOfTransport.feeder][
            StorageRequirement.standard]
        self.assertEqual(
            truck_arrival_distribution.minimum_dwell_time_in_hours,
            dwell_time_distribution.minimum
        )
        self.assertEqual(
            truck_arrival_distribution.considered_time_window_in_hours,
            int(math.floor(dwell_time_distribution.maximum) - math.ceil(dwell_time_distribution.minimum)),
            "Import movement means the truck can come later than minimum but must be earlier than maximum"
        )
