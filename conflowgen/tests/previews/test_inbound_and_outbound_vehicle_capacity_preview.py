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
from conflowgen.previews.inbound_and_outbound_vehicle_capacity_preview import \
    InboundAndOutboundVehicleCapacityPreview
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestInboundAndOutboundVehicleCapacityPreview(unittest.TestCase):
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

        self.preview = InboundAndOutboundVehicleCapacityPreview(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.2
        )

    def test_inbound_with_no_schedules(self):
        """If no schedules are provided, no capacity is needed"""
        empty_capacity = self.preview.get_inbound_capacity_of_vehicles().teu
        self.assertSetEqual(set(ModeOfTransport), set(empty_capacity.keys()))
        for mode_of_transport in ModeOfTransport:
            capacity_in_teu = empty_capacity[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)

    def test_inbound_with_single_arrival_schedules(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        capacity_with_one_feeder = self.preview.get_inbound_capacity_of_vehicles().teu
        self.assertSetEqual(set(ModeOfTransport), set(capacity_with_one_feeder.keys()))
        uninvolved_vehicles = (
                set(ModeOfTransport.get_scheduled_vehicles())
                - {ModeOfTransport.feeder, ModeOfTransport.truck}
        )
        for mode_of_transport in uninvolved_vehicles:
            capacity_in_teu = capacity_with_one_feeder[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)
        inbound_capacity_of_feeder_in_teu = capacity_with_one_feeder[ModeOfTransport.feeder]
        self.assertEqual(inbound_capacity_of_feeder_in_teu, 300)

        # based on the seeded ModeOfTransportDistribution, the following value might vary
        inbound_capacity_of_trucks_in_teu = capacity_with_one_feeder[ModeOfTransport.truck]
        self.assertGreater(inbound_capacity_of_trucks_in_teu, 0)
        self.assertLess(inbound_capacity_of_trucks_in_teu, 300)

    def test_inbound_with_several_arrivals_schedules(self):
        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300
        )
        capacity_with_one_feeder = self.preview.get_inbound_capacity_of_vehicles().teu
        self.assertSetEqual(set(ModeOfTransport), set(capacity_with_one_feeder.keys()))
        uninvolved_vehicles = (
                set(ModeOfTransport.get_scheduled_vehicles())
                - {ModeOfTransport.feeder, ModeOfTransport.truck}
        )
        for mode_of_transport in uninvolved_vehicles:
            capacity_in_teu = capacity_with_one_feeder[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)
        inbound_capacity_of_feeder_in_teu = capacity_with_one_feeder[ModeOfTransport.feeder]
        self.assertEqual(inbound_capacity_of_feeder_in_teu, 600)

        # based on the seeded ModeOfTransportDistribution, this value might vary if not properly set
        inbound_capacity_of_trucks_in_teu = capacity_with_one_feeder[ModeOfTransport.truck]
        self.assertAlmostEqual(inbound_capacity_of_trucks_in_teu, 120)

    def test_outbound_average_capacity_with_several_arrivals_schedules(self):
        """`capacity_with_one_feeder, _ = self.preview.get_outbound_capacity_of_vehicles()` is the key difference!"""
        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300
        )
        capacities = self.preview.get_outbound_capacity_of_vehicles()
        capacity_with_one_feeder = capacities.used.teu
        self.assertSetEqual(set(ModeOfTransport), set(capacity_with_one_feeder.keys()))

        uninvolved_vehicles = (
                set(ModeOfTransport.get_scheduled_vehicles())
                - {ModeOfTransport.feeder, ModeOfTransport.truck}
        )
        for mode_of_transport in uninvolved_vehicles:
            capacity_in_teu = capacity_with_one_feeder[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)

        feeder_vessel_capacity_in_teu = capacity_with_one_feeder[ModeOfTransport.feeder]
        self.assertEqual(feeder_vessel_capacity_in_teu, 600)

        # based on the seeded ModeOfTransportDistribution, this value might vary if not properly set
        truck_capacity_in_teu = capacity_with_one_feeder[ModeOfTransport.truck]
        self.assertGreater(truck_capacity_in_teu, 0)
        self.assertLess(truck_capacity_in_teu, feeder_vessel_capacity_in_teu)
        self.assertAlmostEqual(truck_capacity_in_teu, 120, msg="20% of feeder traffic goes to trucks (600*0.2)")

    def test_outbound_maximum_capacity_with_several_arrivals_schedules(self):
        """`_, capacity_with_one_feeder = self.preview.get_outbound_capacity_of_vehicles()` is the key difference!"""
        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=400,
            average_moved_capacity=300
        )
        capacity_with_one_feeder = self.preview.get_outbound_capacity_of_vehicles().maximum.teu
        self.assertSetEqual(set(ModeOfTransport), set(capacity_with_one_feeder.keys()))

        uninvolved_vehicles = (
                set(ModeOfTransport.get_scheduled_vehicles())
                - {ModeOfTransport.feeder, ModeOfTransport.truck}
        )
        for mode_of_transport in uninvolved_vehicles:
            capacity_in_teu = capacity_with_one_feeder[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)

        feeder_vessel_capacity_in_teu = capacity_with_one_feeder[ModeOfTransport.feeder]
        self.assertEqual(feeder_vessel_capacity_in_teu, 720)

        # based on the seeded ModeOfTransportDistribution, this value might vary if not properly set
        truck_capacity_in_teu = capacity_with_one_feeder[ModeOfTransport.truck]
        self.assertTrue(
            np.isnan(truck_capacity_in_teu),
            "There is no maximum capacity for trucks, they are generated as they are needed."
        )
