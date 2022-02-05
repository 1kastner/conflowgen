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
from conflowgen.posthoc_analyses.container_flow_by_vehicle_type_analysis import ContainerFlowByVehicleTypeAnalysis
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowByVehicleTypeAnalysis(unittest.TestCase):
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
        self.analysis = ContainerFlowByVehicleTypeAnalysis()

    def test_with_no_data(self):
        """If no containers exist, everything is zero"""
        inbound_to_outbound_flow = self.analysis.get_inbound_to_outbound_flow()
        self.assertSetEqual(set(ModeOfTransport), set(inbound_to_outbound_flow.keys()))
        for outbound_flow in inbound_to_outbound_flow.values():
            self.assertSetEqual(set(ModeOfTransport), set(outbound_flow.keys()))

        for inbound_capacities in inbound_to_outbound_flow.values():
            for outbound_capacity in inbound_capacities.values():
                self.assertEqual(outbound_capacity, 0)

    def test_with_single_feeder(self):
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

        inbound_to_outbound_flow = self.analysis.get_inbound_to_outbound_flow()
        self.assertSetEqual(set(ModeOfTransport), set(inbound_to_outbound_flow.keys()))
        for outbound_flow in inbound_to_outbound_flow.values():
            self.assertSetEqual(set(ModeOfTransport), set(outbound_flow.keys()))

        for inbound_vehicle_type, inbound_capacities in inbound_to_outbound_flow.items():
            for outbound_vehicle_type, outbound_capacity in inbound_capacities.items():
                if inbound_vehicle_type == ModeOfTransport.feeder and outbound_vehicle_type == ModeOfTransport.truck:
                    continue
                self.assertEqual(outbound_capacity, 0, f"{inbound_vehicle_type} to {outbound_vehicle_type} must be 0")
        feeder_to_truck = inbound_to_outbound_flow[ModeOfTransport.feeder][ModeOfTransport.truck]
        self.assertEqual(feeder_to_truck, 1, "We just created one container some lines before")
