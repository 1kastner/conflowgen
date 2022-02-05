import unittest

from conflowgen.database_connection.create_tables import create_tables
from conflowgen.domain_models.distribution_seeders import seed_all_distributions
from conflowgen.posthoc_analyses import run_all_posthoc_analyses
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestRunAllPosthocAnalyses(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        create_tables(self.sqlite_db)
        seed_all_distributions()

    def test_with_no_data(self):
        with self.assertLogs('conflowgen', level='INFO') as cm:
            run_all_posthoc_analyses()
        self.assertEqual(len(cm.output), 29)
