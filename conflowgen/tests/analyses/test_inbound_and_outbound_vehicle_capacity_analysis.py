import datetime
import unittest

import numpy as np

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.analyses.inbound_and_outbound_vehicle_capacity_analysis import \
    InboundAndOutboundVehicleCapacityAnalysis
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestInboundAndOutboundVehicleCapacityAnalysis(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            Container,
            LargeScheduledVehicle,
            Truck,
            Feeder,
            ModeOfTransportDistribution,
            Destination
        ])
        mode_of_transport_distribution_seeder.seed()
        self.analysis = InboundAndOutboundVehicleCapacityAnalysis(
            transportation_buffer=0.2
        )

    def test_inbound_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        empty_capacity = self.analysis.get_inbound_capacity_of_vehicles()
        self.assertSetEqual(set(ModeOfTransport), set(empty_capacity.keys()))
        for mode_of_transport in ModeOfTransport:
            capacity_in_teu = empty_capacity[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)

    def test_outbound_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        (empty_capacity, empty_max_capacity) = self.analysis.get_outbound_capacity_of_vehicles()
        for capacity in (empty_capacity, empty_max_capacity):
            self.assertSetEqual(set(ModeOfTransport), set(capacity.keys()))
            for mode_of_transport in set(ModeOfTransport) - {ModeOfTransport.truck}:
                capacity_in_teu = capacity[mode_of_transport]
                self.assertEqual(capacity_in_teu, 0, f"capacity of {mode_of_transport} is unequal 0")

        self.assertEqual(empty_capacity[ModeOfTransport.truck], 0)
        self.assertTrue(np.isnan(empty_max_capacity[ModeOfTransport.truck]))

    def test_inbound_with_single_feeder(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )
        feeder_lsv.save()
        feeder = Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        feeder.save()
        container = Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )
        container.save()

        capacity_with_one_feeder = self.analysis.get_inbound_capacity_of_vehicles()
        self.assertSetEqual(set(ModeOfTransport), set(capacity_with_one_feeder.keys()))
        uninvolved_vehicles = (
                set(ModeOfTransport.get_scheduled_vehicles())
                - {ModeOfTransport.feeder}
        )
        for mode_of_transport in uninvolved_vehicles:
            capacity_in_teu = capacity_with_one_feeder[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)
        inbound_capacity_of_feeder_in_teu = capacity_with_one_feeder[ModeOfTransport.feeder]
        self.assertEqual(inbound_capacity_of_feeder_in_teu, 1)

    def test_outbound_with_single_feeder(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )
        Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )

        capacity_actual, capacity_maximum = self.analysis.get_outbound_capacity_of_vehicles()
        self.assertSetEqual(set(ModeOfTransport), set(capacity_actual.keys()))
        self.assertSetEqual(set(ModeOfTransport), set(capacity_maximum.keys()))

        for mode_of_transport in set(ModeOfTransport) - {ModeOfTransport.truck}:
            capacity_in_teu = capacity_actual[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0, f"{mode_of_transport} has loaded more than expected")
        outbound_actual_capacity_of_feeder_in_teu = capacity_actual[ModeOfTransport.truck]
        self.assertEqual(outbound_actual_capacity_of_feeder_in_teu, 1)

        for mode_of_transport in set(ModeOfTransport) - {ModeOfTransport.feeder, ModeOfTransport.truck}:
            capacity_in_teu = capacity_maximum[mode_of_transport]
            self.assertEqual(capacity_in_teu, 0)
        outbound_max_capacity_of_feeder_in_teu = capacity_maximum[ModeOfTransport.feeder]
        self.assertEqual(outbound_max_capacity_of_feeder_in_teu, 300)
        outbound_max_capacity_of_trucks_in_teu = capacity_maximum[ModeOfTransport.truck]
        self.assertTrue(np.isnan(outbound_max_capacity_of_trucks_in_teu))
