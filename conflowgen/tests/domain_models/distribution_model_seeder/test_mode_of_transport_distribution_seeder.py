"""
Check if mode of transportation is properly translated between application and database.
"""

import unittest

from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestModeOfTransportationDistributionSeeder(unittest.TestCase):
    """
    The actual ModeOfTransportField behavior is implemented in peewee.
    """

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ModeOfTransportDistribution
        ])

    def test_seeding(self):
        """The seed method includes a verification at the end and throws an error in case of a problem."""
        mode_of_transport_distribution_seeder.seed()
