import unittest

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.posthoc_analysis.container_flow_adjustment_by_vehicle_type_analysis import \
    ContainerFlowAdjustmentByVehicleTypeAnalysis
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowAdjustmentByVehicleTypeAnalysis(unittest.TestCase):
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
        self.analysis = ContainerFlowAdjustmentByVehicleTypeAnalysis()

    def test_with_no_data(self):
        """If no containers exist, everything is zero"""
        initial_to_adjusted_outbound_flow = self.analysis.get_initial_to_adjusted_outbound_flow()
        initial_to_adjusted_outbound_flow_in_containers = initial_to_adjusted_outbound_flow.containers
        initial_to_adjusted_outbound_flow_in_teu = initial_to_adjusted_outbound_flow.TEU

        self.assertSetEqual(set(ModeOfTransport), set(initial_to_adjusted_outbound_flow_in_containers.keys()))
        self.assertSetEqual(set(ModeOfTransport), set(initial_to_adjusted_outbound_flow_in_teu.keys()))

        for adjustment_flow in initial_to_adjusted_outbound_flow_in_containers.values():
            self.assertSetEqual(set(ModeOfTransport), set(adjustment_flow.keys()))
        for adjustment_flow in initial_to_adjusted_outbound_flow_in_teu.values():
            self.assertSetEqual(set(ModeOfTransport), set(adjustment_flow.keys()))

        for initial_capacities in initial_to_adjusted_outbound_flow_in_containers.values():
            for adjusted_capacity in initial_capacities.values():
                self.assertEqual(adjusted_capacity, 0)
        for initial_capacities in initial_to_adjusted_outbound_flow_in_teu.values():
            for adjusted_capacity in initial_capacities.values():
                self.assertEqual(adjusted_capacity, 0)

    def test_with_single_truck(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=None,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )

        initial_to_adjusted_outbound_flow = self.analysis.get_initial_to_adjusted_outbound_flow()
        initial_to_adjusted_outbound_flow_in_containers = initial_to_adjusted_outbound_flow.containers
        initial_to_adjusted_outbound_flow_in_teu = initial_to_adjusted_outbound_flow.TEU

        self.assertSetEqual(set(ModeOfTransport), set(initial_to_adjusted_outbound_flow_in_containers.keys()))
        for adjustment_flow in initial_to_adjusted_outbound_flow_in_containers.values():
            self.assertSetEqual(set(ModeOfTransport), set(adjustment_flow.keys()))
        self.assertSetEqual(set(ModeOfTransport), set(initial_to_adjusted_outbound_flow_in_teu.keys()))
        for adjustment_flow in initial_to_adjusted_outbound_flow_in_teu.values():
            self.assertSetEqual(set(ModeOfTransport), set(adjustment_flow.keys()))

        for initial_vehicle_type, initial_capacities in initial_to_adjusted_outbound_flow_in_containers.items():
            for adjusted_vehicle_type, adjusted__capacity in initial_capacities.items():
                if initial_vehicle_type == ModeOfTransport.truck and adjusted_vehicle_type == ModeOfTransport.truck:
                    continue
                self.assertEqual(adjusted__capacity, 0, f"{initial_vehicle_type} to {adjusted_vehicle_type} must be 0 "
                                                        f"containers")
        for initial_vehicle_type, initial_capacities in initial_to_adjusted_outbound_flow_in_teu.items():
            for adjusted_vehicle_type, adjusted__capacity in initial_capacities.items():
                if initial_vehicle_type == ModeOfTransport.truck and adjusted_vehicle_type == ModeOfTransport.truck:
                    continue
                self.assertEqual(adjusted__capacity, 0, f"{initial_vehicle_type} to {adjusted_vehicle_type} must be 0 "
                                                        f"TEU")
        truck_to_truck = initial_to_adjusted_outbound_flow_in_containers[ModeOfTransport.truck][ModeOfTransport.truck]
        self.assertEqual(truck_to_truck, 1, "We just created one container some lines before")
        truck_to_truck = initial_to_adjusted_outbound_flow_in_teu[ModeOfTransport.truck][ModeOfTransport.truck]
        self.assertEqual(truck_to_truck, 1, "We just created one TEU some lines before")

    def test_with_truck_and_feeder(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=None,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )
        Container.create(
            weight=20,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=None,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.feeder
        )

        initial_to_adjusted_outbound_flow = self.analysis.get_initial_to_adjusted_outbound_flow()
        initial_to_adjusted_outbound_flow_in_containers = initial_to_adjusted_outbound_flow.containers
        initial_to_adjusted_outbound_flow_in_teu = initial_to_adjusted_outbound_flow.TEU

        self.assertSetEqual(set(ModeOfTransport), set(initial_to_adjusted_outbound_flow_in_containers.keys()))
        for adjustment_flow in initial_to_adjusted_outbound_flow_in_containers.values():
            self.assertSetEqual(set(ModeOfTransport), set(adjustment_flow.keys()))
        self.assertSetEqual(set(ModeOfTransport), set(initial_to_adjusted_outbound_flow_in_teu.keys()))
        for adjustment_flow in initial_to_adjusted_outbound_flow_in_teu.values():
            self.assertSetEqual(set(ModeOfTransport), set(adjustment_flow.keys()))

        for initial_vehicle_type, initial_capacities in initial_to_adjusted_outbound_flow_in_containers.items():
            for adjusted_vehicle_type, adjusted__capacity in initial_capacities.items():
                if initial_vehicle_type == ModeOfTransport.truck and adjusted_vehicle_type == ModeOfTransport.truck:
                    continue
                if initial_vehicle_type == ModeOfTransport.feeder and adjusted_vehicle_type == ModeOfTransport.truck:
                    continue
                self.assertEqual(adjusted__capacity, 0, f"{initial_vehicle_type} to {adjusted_vehicle_type} must be 0 "
                                                        f"containers")
        for initial_vehicle_type, initial_capacities in initial_to_adjusted_outbound_flow_in_teu.items():
            for adjusted_vehicle_type, adjusted__capacity in initial_capacities.items():
                if initial_vehicle_type == ModeOfTransport.truck and adjusted_vehicle_type == ModeOfTransport.truck:
                    continue
                if initial_vehicle_type == ModeOfTransport.feeder and adjusted_vehicle_type == ModeOfTransport.truck:
                    continue
                self.assertEqual(adjusted__capacity, 0, f"{initial_vehicle_type} to {adjusted_vehicle_type} must be 0 "
                                                        f"TEU")

        feeder_to_truck = initial_to_adjusted_outbound_flow_in_containers[ModeOfTransport.feeder][ModeOfTransport.truck]
        self.assertEqual(feeder_to_truck, 1, "One 40' container (from feeder to truck) has been created previously")
        feeder_to_truck = initial_to_adjusted_outbound_flow_in_teu[ModeOfTransport.feeder][ModeOfTransport.truck]
        self.assertEqual(feeder_to_truck, 2, "One 40' container (from feeder to truck) has been created previously")

        truck_to_truck = initial_to_adjusted_outbound_flow_in_containers[ModeOfTransport.truck][ModeOfTransport.truck]
        self.assertEqual(truck_to_truck, 1, "One 20' container (from truck to truck) has been created previously")
        truck_to_truck = initial_to_adjusted_outbound_flow_in_teu[ModeOfTransport.truck][ModeOfTransport.truck]
        self.assertEqual(truck_to_truck, 1, "One 20' container (from truck to truck) has been created previously")
