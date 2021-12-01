"""
Check if container weights can be properly seeded.
"""

import unittest

from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_seeders import truck_arrival_distribution_seeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckArrivalDistributionSeeder(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            TruckArrivalDistribution
        ])

    def test_seeding(self):
        """This should just not throw any exception"""
        truck_arrival_distribution_seeder.seed()
