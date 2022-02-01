import unittest
import datetime

from conflowgen.api.container_flow_generation_manager import ContainerFlowGenerationManager
from conflowgen.database_connection.create_tables import create_tables
from conflowgen.domain_models.distribution_seeders import seed_all_distributions
from conflowgen.previews import run_all_previews
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestRunAllPreviews(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        create_tables(self.sqlite_db)
        seed_all_distributions()
        container_flow_generation_manager = ContainerFlowGenerationManager()
        container_flow_generation_manager.set_properties(
            name="Test previews",
            start_date=datetime.datetime.now().date(),
            end_date=datetime.datetime.now().date() + datetime.timedelta(days=21)
        )

    def test_with_no_data(self):
        with self.assertLogs('conflowgen', level='INFO') as cm:
            run_all_previews()
        self.maxDiff = None
        self.assertEqual(len(cm.output), 14)

        # Test only some entries. The detailed tests should be done in the unit test of the respective report.
        self.assertEqual(
            cm.output[0],
            "INFO:conflowgen:Run all previews for the input distributions in combination with the schedules."
        )
        self.assertEqual(
            cm.output[1],
            "INFO:conflowgen:\nInboundAndOutboundVehicleCapacityPreviewReport\n"
        )
        self.assertEqual(
            cm.output[-1],
            'INFO:conflowgen:All previews have been presented.'
        )
