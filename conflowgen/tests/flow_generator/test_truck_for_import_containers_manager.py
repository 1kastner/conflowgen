from __future__ import annotations

import datetime
import math
import random
import unittest
import unittest.mock
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.api.container_dwell_time_distribution_manager import ContainerDwellTimeDistributionManager
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForPickup
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from conflowgen.domain_models.distribution_seeders import truck_arrival_distribution_seeder, \
    container_dwell_time_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
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
            Destination,
            Schedule,
            TruckArrivalInformationForPickup
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

    def visualize_probabilities(self, container: Container, drawn_times, container_arrival_time: datetime.datetime):
        import inspect  # pylint: disable=import-outside-toplevel
        import seaborn as sns  # pylint: disable=import-outside-toplevel
        container_dwell_time_distribution, _ = self._get_distribution(container)
        sns.kdeplot(drawn_times, bw=0.01).set(title='Triggered from: ' + inspect.stack()[1].function)

        start_date = container_arrival_time.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)

        plt.axvline(x=start_date + datetime.timedelta(hours=container_dwell_time_distribution.minimum))
        plt.axvline(x=start_date + datetime.timedelta(hours=container_dwell_time_distribution.maximum))
        plt.axvline(x=start_date, color="k")

        x = np.linspace(
            0,
            int(container_dwell_time_distribution.maximum),
            int(container_dwell_time_distribution.maximum)
        )

        x_in_range = x[np.where(
            (container_dwell_time_distribution.minimum < x) & (x < container_dwell_time_distribution.maximum)
        )]
        ax2 = plt.gca().twinx()
        probs = container_dwell_time_distribution.get_probabilities(x_in_range, reversed_distribution=True)

        ax2.plot(
            [container_arrival_time + datetime.timedelta(hours=h) for h in x_in_range],
            probs,
            color='gray',
            lw=5,
            alpha=0.9,
        )

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

        self.assertEqual(216, container_dwell_time_distribution.maximum)

        possible_hours_for_truck_arrival = truck_arrival_distribution.size_of_time_window_in_hours
        self.assertEqual(
            216,
            possible_hours_for_truck_arrival,
            "The truck might arrive 216h after the arrival of the container, but not within the first three hours. "
            "Furthermore, the last hour is subtracted because up to 59 minutes are later added again and the maximum "
            "should not be surpassed."
        )

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
        dwell_time_distribution = self.container_dwell_time_distributions_from_x_to_truck[
            ModeOfTransport.deep_sea_vessel]
        dwell_time_distribution_for_standard_container = dwell_time_distribution[StorageRequirement.standard]
        minimum_dwell_time = dwell_time_distribution_for_standard_container.minimum
        maximum_dwell_time = dwell_time_distribution_for_standard_container.maximum

        pickup_times = []
        for _ in range(1000):
            pickup_time = self.get_pickup_time(container, container_arrival_time)
            dwell_time = (pickup_time - container_arrival_time).total_seconds() / 3600
            self.assertGreaterEqual(dwell_time, minimum_dwell_time)
            self.assertLessEqual(dwell_time, maximum_dwell_time)
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
        dwell_time_distribution = self.container_dwell_time_distributions_from_x_to_truck[
            ModeOfTransport.deep_sea_vessel]
        dwell_time_distribution_for_standard_container = dwell_time_distribution[StorageRequirement.standard]
        minimum_dwell_time = dwell_time_distribution_for_standard_container.minimum
        maximum_dwell_time = dwell_time_distribution_for_standard_container.maximum

        pickup_times = []
        for _ in range(1000):
            pickup_time = self.get_pickup_time(container, container_arrival_time)
            dwell_time = (pickup_time - container_arrival_time).total_seconds() / 3600
            self.assertGreaterEqual(dwell_time, minimum_dwell_time)
            self.assertLessEqual(dwell_time, maximum_dwell_time)

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
            truck_arrival_distribution.size_of_time_window_in_hours,
            int(math.floor(dwell_time_distribution.maximum)),
            "Import movement means the truck can come later than minimum but must be earlier than maximum"
        )

    def test_nothing_to_do(self):
        with unittest.mock.patch.object(
                self.manager.vehicle_factory, "create_truck", return_value=None) as create_truck_method:
            self.manager.generate_trucks_for_picking_up()

        create_truck_method.assert_not_called()

    def test_happy_path(self):
        container_arrival_time = datetime.datetime(
            year=2022, month=8, day=10
        )
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name="TestDeepSeaService",
            vehicle_arrives_at=container_arrival_time.date(),
            vehicle_arrives_at_time=container_arrival_time.time(),
            average_vehicle_capacity=5000,
            average_moved_capacity=1200,
        )
        lsv = LargeScheduledVehicle.create(
            vehicle_name="TestDeepSeaVessel",
            capacity_in_teu=schedule.average_vehicle_capacity,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=container_arrival_time,
            schedule=schedule
        )

        self._use_uniform_distribution()

        for _ in range(1000):
            Container.create(
                delivered_by=ModeOfTransport.deep_sea_vessel,
                delivered_by_large_scheduled_vehicle=lsv,
                picked_up_by=ModeOfTransport.truck,
                picked_up_by_initial=ModeOfTransport.truck,
                storage_requirement=StorageRequirement.standard,
                weight=random.randint(2, 30),
                length=ContainerLength.twenty_feet
            )

        with unittest.mock.patch.object(
                self.manager.vehicle_factory, "create_truck", return_value=None) as create_truck_method:
            self.manager.generate_trucks_for_picking_up()

        self.assertEqual(create_truck_method.call_count, 1000)

    @staticmethod
    def _use_uniform_distribution():
        container_dwell_time_distribution_manager = ContainerDwellTimeDistributionManager()
        container_dwell_time_distributions = container_dwell_time_distribution_manager. \
            get_container_dwell_time_distribution()
        new_distribution = {}
        for inbound_vehicle in ModeOfTransport:
            new_distribution[inbound_vehicle] = {}
            for outbound_vehicle in ModeOfTransport:
                new_distribution[inbound_vehicle][outbound_vehicle] = {}
                for storage_requirement in StorageRequirement:
                    distribution = container_dwell_time_distributions[inbound_vehicle][outbound_vehicle][
                        storage_requirement]
                    distribution_dict = distribution.to_dict()
                    distribution_dict["distribution_name"] = "uniform"
                    new_distribution[inbound_vehicle][outbound_vehicle][storage_requirement] = distribution_dict
        container_dwell_time_distribution_manager.set_container_dwell_time_distribution(new_distribution)

    def test_helper_drop_where_zero(self):
        cleaned = self.manager._drop_where_zero([1, 2, 3], [0, 0, 1])  # pylint: disable=protected-access
        self.assertListEqual([3], cleaned)

        cleaned = self.manager._drop_where_zero([1, 2, 3], [1, 0, 1])  # pylint: disable=protected-access
        self.assertListEqual([1, 3], cleaned)

        cleaned = self.manager._drop_where_zero([1, 2, 3], [0, 1, 1])  # pylint: disable=protected-access
        self.assertListEqual([2, 3], cleaned)

    def test_pickup_time_minimum(self):
        container_arrival_time = datetime.datetime(
            year=2021, month=8, day=6, hour=12, minute=19  # a Monday
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )

        # pylint: disable=protected-access
        pickup_time = self.manager._get_container_pickup_time(
            container, container_arrival_time, _debug_check_distribution_property="minimum"
        )

        distribution = self.manager.container_dwell_time_distributions[
            ModeOfTransport.deep_sea_vessel][ModeOfTransport.truck][StorageRequirement.standard]
        self.assertEqual(3, distribution.minimum)

        minimum = datetime.datetime(2021, 8, 6, 16)  # 12:19 -> 13:00 -> 16:00
        self.assertEqual(minimum, pickup_time)

        container_dwell_time = (minimum - container_arrival_time).total_seconds() / 3600
        self.assertGreater(distribution.maximum, container_dwell_time)
        self.assertLess(distribution.minimum, container_dwell_time)

    def test_pickup_time_maximum(self):
        container_arrival_time = datetime.datetime(
            year=2021, month=8, day=8, hour=12, minute=13  # a Monday
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )

        # pylint: disable=protected-access
        pickup_time = self.manager._get_container_pickup_time(
            container, container_arrival_time, _debug_check_distribution_property="maximum"
        )

        distribution_1 = self.manager.container_dwell_time_distributions[
            ModeOfTransport.deep_sea_vessel][ModeOfTransport.truck][StorageRequirement.standard]
        self.assertEqual(216, distribution_1.maximum)

        distribution_2 = self.manager.truck_arrival_distributions[
            ModeOfTransport.deep_sea_vessel][StorageRequirement.standard]
        distribution_2_maximum = distribution_2.size_of_time_window_in_hours
        self.assertEqual(216, distribution_2_maximum)

        # One might think that 215h59min would be a better choice. However, the earliest feasible time is 13:00 because
        # in the truck arrival distribution we only account for full hours. That means we already have 47 minutes of
        # waiting on the clock, and we do not want to go beyond the maximum dwell time of 216h
        maximum = datetime.datetime(2021, 8, 8, 13) + datetime.timedelta(hours=214, minutes=59)
        self.assertEqual(maximum, pickup_time)

        containder_dwell_time = (maximum - container_arrival_time).total_seconds() / 3600
        self.assertGreater(distribution_1.maximum, containder_dwell_time)
        self.assertLess(distribution_1.minimum, containder_dwell_time)

    def test_pickup_time_average(self):
        container_arrival_time = datetime.datetime(
            year=2021, month=8, day=8, hour=12, minute=13  # a Monday
        )
        container: Container = Container.create(
            delivered_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck,
            storage_requirement=StorageRequirement.standard,
            weight=23,
            length=ContainerLength.twenty_feet
        )

        # pylint: disable=protected-access
        pickup_time = self.manager._get_container_pickup_time(
            container, container_arrival_time, _debug_check_distribution_property="average"
        )

        distribution = self.manager.container_dwell_time_distributions[
            ModeOfTransport.deep_sea_vessel][ModeOfTransport.truck][StorageRequirement.standard]
        self.assertEqual(72, distribution.average)

        average = datetime.datetime(2021, 8, 8, 13) + datetime.timedelta(hours=72)
        self.assertEqual(average, pickup_time)

        containder_dwell_time = (average - container_arrival_time).total_seconds() / 3600
        self.assertGreater(distribution.maximum, containder_dwell_time)
        self.assertLess(distribution.minimum, containder_dwell_time)
