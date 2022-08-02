import unittest

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.analyses.container_flow_adjustment_by_vehicle_type_analysis_summary import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummary
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowAdjustmentByVehicleTypeAnalysisSummary(unittest.TestCase):
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
        self.analysis_summary = ContainerFlowAdjustmentByVehicleTypeAnalysisSummary()

    def test_with_no_data(self):
        """If no containers exist, everything is zero"""
        adjusted_to = self.analysis_summary.get_summary()
        self.assertEqual(sum(adjusted_to), 0)

    def test_with_single_unchanged_vehicle(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=None,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )
        adjusted_to = self.analysis_summary.get_summary()
        self.assertEqual(adjusted_to.unchanged, 1)
        self.assertSetEqual(set(adjusted_to), {0, 1})
        self.assertEqual(sum(adjusted_to), 1)

    def test_with_single_changed_vehicle(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=None,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel
        )
        adjusted_to = self.analysis_summary.get_summary()
        self.assertEqual(adjusted_to.feeder, 1)
        self.assertSetEqual(set(adjusted_to), {0, 1})
        self.assertEqual(sum(adjusted_to), 1)
