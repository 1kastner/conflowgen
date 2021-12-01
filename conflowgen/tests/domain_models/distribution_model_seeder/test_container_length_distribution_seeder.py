"""
Check if container weights can be properly seeded.
"""

import unittest

from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_seeders import container_length_distribution_seeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerLengthDistributionSeeder(unittest.TestCase):
    """
    The actual ModeOfTransportField behavior is implemented in peewee.
    """

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ContainerLengthDistribution
        ])

    def test_seeding(self):
        """This should just not throw any exception"""
        container_length_distribution_seeder.seed()
