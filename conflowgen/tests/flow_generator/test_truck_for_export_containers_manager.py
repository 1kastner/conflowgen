from __future__ import annotations

import datetime
import math
import random
import unittest
import unittest.mock
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np

from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery
from conflowgen.flow_generator.truck_for_export_containers_manager import \
    TruckForExportContainersManager
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.api.container_dwell_time_distribution_manager import ContainerDwellTimeDistributionManager
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
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db
from conflowgen.tools.continuous_distribution import ContinuousDistribution
from conflowgen.tools.weekly_distribution import WeeklyDistribution


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
            LargeScheduledVehicle,
            Schedule,
            TruckArrivalInformationForDelivery
        ])
        truck_arrival_distribution_seeder.seed()
        container_dwell_time_distribution_seeder.seed()

        container_dwell_time_distributions = ContainerDwellTimeDistributionRepository.get_distributions()
        self.container_dwell_time_distributions_from_truck_to = container_dwell_time_distributions[
            ModeOfTransport.truck]

        # Enables visualisation, helpful for probability distributions.
        # However, this blocks the execution of tests.
        self.visual_debug = False

        self.manager = TruckForExportContainersManager()
        self.manager.reload_distributions()

    def visualize_probabilities(self, container: Container, drawn_times, container_departure_time):
        import inspect  # pylint: disable=import-outside-toplevel
        import seaborn as sns  # pylint: disable=import-outside-toplevel
        container_dwell_time_distribution, _ = self._get_distributions(container)
        sns.kdeplot(drawn_times, bw=0.01).set(title='Triggered from: ' + inspect.stack()[1].function)
        plt.axvline(x=container_departure_time, color="k")
        plt.axvline(x=container_departure_time - datetime.timedelta(hours=container_dwell_time_distribution.minimum))
        plt.axvline(x=container_departure_time - datetime.timedelta(hours=container_dwell_time_distribution.maximum))

        x = np.linspace(
            0,
            int(container_dwell_time_distribution.maximum),
            int(container_dwell_time_distribution.maximum)
        )

        x_in_range = x[np.where(
            (container_dwell_time_distribution.minimum < x) & (x < container_dwell_time_distribution.maximum)
        )]
        ax2 = plt.gca().twinx()
        probs = container_dwell_time_distribution.get_probabilities(x_in_range)

        ax2.plot(
            [container_departure_time - datetime.timedelta(hours=h) for h in x_in_range],
            probs,
            color='gray',
            lw=5,
            alpha=0.9,
        )

        plt.show(block=True)

    def _get_distributions(self, container: Container) -> tuple[ContinuousDistribution, WeeklyDistribution | None]:

        # pylint: disable=protected-access
        container_dwell_time_distribution, truck_arrival_distribution = self.manager._get_distributions(container)

        return container_dwell_time_distribution, truck_arrival_distribution

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
        dwell_time_distribution = self.container_dwell_time_distributions_from_truck_to[ModeOfTransport.deep_sea_vessel]
        dwell_time_distribution_for_standard_container = dwell_time_distribution[StorageRequirement.standard]
        minimum_dwell_time = dwell_time_distribution_for_standard_container.minimum
        maximum_dwell_time = dwell_time_distribution_for_standard_container.maximum
        delivery_times = []
        for i in range(1000):
            # pylint: disable=protected-access
            delivery_time = self.manager._get_container_delivery_time(container, container_departure_time)

            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertTrue(delivery_time.weekday() != 6,
                            f"containers do not arrive on Sundays, but here we had {delivery_time} in round {i + 1}")
            delivery_times.append(delivery_time)

            dwell_time = (container_departure_time - delivery_time).total_seconds() / 3600
            self.assertGreaterEqual(dwell_time, minimum_dwell_time)
            self.assertLessEqual(dwell_time, maximum_dwell_time)

        if self.visual_debug:
            self.visualize_probabilities(container, delivery_times, container_departure_time)

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
        dwell_time_distribution = self.container_dwell_time_distributions_from_truck_to[ModeOfTransport.deep_sea_vessel]
        dwell_time_distribution_for_standard_container = dwell_time_distribution[StorageRequirement.standard]
        minimum_dwell_time = dwell_time_distribution_for_standard_container.minimum
        maximum_dwell_time = dwell_time_distribution_for_standard_container.maximum

        delivery_times = []
        for i in range(1000):
            # pylint: disable=protected-access
            delivery_time = self.manager._get_container_delivery_time(container, container_departure_time)

            delivery_times.append(delivery_time)
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertTrue(delivery_time.weekday() != 6,
                            f"containers do not arrive on Sundays, but here we had {delivery_time} in round {i + 1}")

            dwell_time = (container_departure_time - delivery_time).total_seconds() / 3600
            self.assertGreaterEqual(dwell_time, minimum_dwell_time)
            self.assertLessEqual(dwell_time, maximum_dwell_time)

        if self.visual_debug:
            self.visualize_probabilities(container, delivery_times, container_departure_time)

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

        dwell_time_distribution = self.container_dwell_time_distributions_from_truck_to[ModeOfTransport.deep_sea_vessel]
        dwell_time_distribution_for_standard_container = dwell_time_distribution[StorageRequirement.standard]
        minimum_dwell_time = dwell_time_distribution_for_standard_container.minimum
        maximum_dwell_time = dwell_time_distribution_for_standard_container.maximum

        delivery_times = []
        for i in range(1000):
            # pylint: disable=protected-access
            delivery_time = self.manager._get_container_delivery_time(container, container_departure_time)

            dwell_time = (container_departure_time - delivery_time).total_seconds() / 3600
            self.assertGreaterEqual(dwell_time, minimum_dwell_time)
            self.assertLessEqual(dwell_time, maximum_dwell_time)

            delivery_times.append(delivery_time)
            self.assertLessEqual(delivery_time, container_departure_time,
                                 "container must not arrive later than their departure time "
                                 f"but here we had {delivery_time} in round {i + 1}")
            self.assertNotEqual(delivery_time.weekday(), 6,
                                f"containers do not arrive on Sundays, "
                                f"but here we had {delivery_time} in round {i + 1}")

        if self.visual_debug:
            self.visualize_probabilities(container, delivery_times, container_departure_time)

        weekday_counter = Counter([delivery_time.weekday() for delivery_time in delivery_times])
        self.assertIn(4, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Friday must be counted (30.07.2021)")
        self.assertIn(5, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Saturday must be counted (31.07.2021)")
        self.assertIn(0, weekday_counter.keys(), "Probability (out of 1000 repetitions): "
                                                 "At least once a Monday must be counted (02.08.2021)")

    def test_distributions_match(self):
        truck_arrival_distribution = self.manager.truck_arrival_distributions[ModeOfTransport.feeder][
            StorageRequirement.standard]
        dwell_time_distribution = self.container_dwell_time_distributions_from_truck_to[ModeOfTransport.feeder][
            StorageRequirement.standard]
        self.assertEqual(
            truck_arrival_distribution.size_of_time_window_in_hours,
            int(math.floor(dwell_time_distribution.maximum))
        )

    def test_nothing_to_do(self):
        with unittest.mock.patch.object(
                self.manager.vehicle_factory, "create_truck", return_value=None) as create_truck_method:
            self.manager.generate_trucks_for_delivering()

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
                delivered_by=ModeOfTransport.truck,
                picked_up_by=ModeOfTransport.deep_sea_vessel,
                picked_up_by_large_scheduled_vehicle=lsv,
                picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
                storage_requirement=StorageRequirement.standard,
                weight=random.randint(2, 30),
                length=ContainerLength.twenty_feet
            )

        with unittest.mock.patch.object(
                self.manager.vehicle_factory, "create_truck", return_value=None) as create_truck_method:
            self.manager.generate_trucks_for_delivering()

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
