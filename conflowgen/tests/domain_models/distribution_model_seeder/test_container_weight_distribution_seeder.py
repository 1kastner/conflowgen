"""
Check if container weights can be properly seeded.
"""

import unittest

from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.distribution_seeders import container_weight_distribution_seeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerWeightDistributionSeeder(unittest.TestCase):
    """
    The actual ModeOfTransportField behavior is implemented in peewee.
    """

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ContainerWeightDistribution
        ])

    def test_seeding(self):
        """This should just not throw any exception"""
        container_weight_distribution_seeder.seed()
