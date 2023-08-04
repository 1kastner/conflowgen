import datetime
import unittest

import numpy as np

from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.api.container_length_distribution_manager import ContainerLengthDistributionManager
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.previews.vehicle_capacity_exceeded_preview import VehicleCapacityExceededPreview
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleCapacityExceededPreview(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            ModeOfTransportDistribution,
            ContainerLengthDistribution
        ])
        now = datetime.datetime.now()
        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions({
            ModeOfTransport.truck: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.train: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.barge: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.feeder: {
                ModeOfTransport.truck: 0.2,
                ModeOfTransport.train: 0.4,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            },
            ModeOfTransport.deep_sea_vessel: {
                ModeOfTransport.truck: 0.2,
                ModeOfTransport.train: 0.4,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            }
        })

        container_length_manager = ContainerLengthDistributionManager()
        container_length_manager.set_container_length_distribution(  # Set default container length distribution
            {
                ContainerLength.other: 0.001,
                ContainerLength.twenty_feet: 0.4,
                ContainerLength.forty_feet: 0.57,
                ContainerLength.forty_five_feet: 0.029
            }
        )

        self.preview = VehicleCapacityExceededPreview(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.2
        )

    def test_with_no_schedules(self):
        """If no schedules are provided, no capacity is needed"""
        no_excess_comparison = self.preview.compare()
        self.assertSetEqual(set(ModeOfTransport), set(no_excess_comparison.keys()))
        for mode_of_transport_from in (set(ModeOfTransport) - {ModeOfTransport.truck}):
            (
                container_capacity_to_pick_up,
                maximum_capacity,
                vehicle_type_capacity_is_exceeded
            ) = no_excess_comparison[mode_of_transport_from]

            self.assertEqual(container_capacity_to_pick_up, 0, msg=f"mode_of_transport_from: {mode_of_transport_from}")
            self.assertEqual(maximum_capacity, 0, msg=f"mode_of_transport_from: {mode_of_transport_from}")
            self.assertFalse(vehicle_type_capacity_is_exceeded, msg=f"mode_of_transport_from: {mode_of_transport_from}")

            mode_of_transport_from = ModeOfTransport.truck
            (
                container_capacity_to_pick_up,
                maximum_capacity,
                vehicle_type_capacity_is_exceeded
            ) = no_excess_comparison[mode_of_transport_from]

            self.assertEqual(container_capacity_to_pick_up, 0, msg=f"mode_of_transport_from: {mode_of_transport_from}")
            self.assertTrue(np.isnan(maximum_capacity), msg=f"mode_of_transport_from: {mode_of_transport_from}")
            self.assertFalse(vehicle_type_capacity_is_exceeded, msg=f"mode_of_transport_from: {mode_of_transport_from}")

    def test_with_single_arrival_schedules(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()

        with_excess_comparison = self.preview.compare()
        self.assertSetEqual(set(ModeOfTransport), set(with_excess_comparison.keys()))
        for mode_of_transport_from in (set(ModeOfTransport) - {ModeOfTransport.truck}):
            (
                container_capacity_to_pick_up,
                maximum_capacity,
                vehicle_type_capacity_is_exceeded
            ) = with_excess_comparison[mode_of_transport_from]

            self.assertGreater(
                container_capacity_to_pick_up, 0, msg=f"mode_of_transport_from: {mode_of_transport_from}")
            self.assertGreaterEqual(maximum_capacity, 0, msg=f"mode_of_transport_from: {mode_of_transport_from}")
            if mode_of_transport_from != ModeOfTransport.feeder:
                self.assertTrue(vehicle_type_capacity_is_exceeded,
                                msg=f"mode_of_transport_from: {mode_of_transport_from}")
            else:
                self.assertFalse(vehicle_type_capacity_is_exceeded, "feeder has sufficient space for taking all "
                                                                    "containers with them again")

        mode_of_transport_from = ModeOfTransport.truck
        (
            container_capacity_to_pick_up,
            maximum_capacity,
            vehicle_type_capacity_is_exceeded
        ) = with_excess_comparison[mode_of_transport_from]

        self.assertAlmostEqual(container_capacity_to_pick_up, 60, msg="20% of 300 is 60")
        self.assertTrue(np.isnan(maximum_capacity), msg=f"mode_of_transport_from: {mode_of_transport_from}")
        self.assertFalse(vehicle_type_capacity_is_exceeded, msg=f"mode_of_transport_from: {mode_of_transport_from}")
