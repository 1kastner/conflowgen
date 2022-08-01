import datetime
import unittest

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.analyses.inbound_to_outbound_vehicle_capacity_utilization_analysis import \
    InboundToOutboundVehicleCapacityUtilizationAnalysis
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestInboundToOutboundCapacityUtilizationAnalysis(unittest.TestCase):
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
        self.analysis = InboundToOutboundVehicleCapacityUtilizationAnalysis(
            transportation_buffer=0.2
        )

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        empty_capacities = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle()
        self.assertDictEqual({}, empty_capacities)

    def test_inbound_with_single_feeder(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=250,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=schedule.average_vehicle_capacity,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )
        feeder_lsv.save()
        feeder = Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        feeder.save()
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.truck
        )

        capacities_with_one_feeder = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle()

        self.assertEqual(len(capacities_with_one_feeder), 1, "There is only one vehicle")

        key_of_entry = list(capacities_with_one_feeder.keys())[0]
        self.assertEqual(len(key_of_entry), 3, "Key consists of three components")
        mode_of_transport, service_name, vehicle_name = key_of_entry
        self.assertEqual(mode_of_transport, ModeOfTransport.feeder)
        self.assertEqual(service_name, "TestFeederService")
        self.assertEqual(vehicle_name, "TestFeeder1")

        value_of_entry = list(capacities_with_one_feeder.values())[0]
        self.assertEqual(len(value_of_entry), 2, "Value consists of two components")
        (used_capacity_on_inbound_journey, used_capacity_on_outbound_journey) = value_of_entry
        self.assertEqual(used_capacity_on_inbound_journey, 250)
        self.assertEqual(used_capacity_on_outbound_journey, 1, "One 20' is loaded")
