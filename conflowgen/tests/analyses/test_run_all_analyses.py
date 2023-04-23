import datetime
import unittest
import unittest.mock

from conflowgen.analyses import run_all_analyses
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.database_connection.create_tables import create_tables
from conflowgen.domain_models.distribution_seeders import seed_all_distributions
from conflowgen.tests.autoclose_matplotlib import UnitTestCaseWithMatplotlib
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestRunAllAnalyses(UnitTestCaseWithMatplotlib):
    def setUp(self) -> None:
        self.sqlite_db = setup_sqlite_in_memory_db()
        create_tables(self.sqlite_db)
        seed_all_distributions()
        ContainerFlowGenerationProperties.create(
            start_date=datetime.datetime(2021, 12, 1),
            end_date=datetime.datetime(2021, 12, 6)
        )

    def test_with_no_data(self):
        with self.assertLogs('conflowgen', level='INFO') as context:
            run_all_analyses()
        self.assertEqual(len(context.output), 35)

    def test_with_no_data_as_graph(self):
        with unittest.mock.patch('matplotlib.pyplot.show'):
            with self.assertLogs('conflowgen', level='INFO') as context:
                run_all_analyses(as_text=False, as_graph=True, static_graphs=True)
        self.assertEqual(len(context.output), 27)
