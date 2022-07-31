"""
Check if mode of transportation is properly translated between application and database.
"""

import unittest

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_seeders import container_dwell_time_distribution_seeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerDwellTimeDistributionSeeder(unittest.TestCase):
    """
    The actual ModeOfTransportField behavior is implemented in peewee.
    """

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ContainerDwellTimeDistribution
        ])

    def test_seeding(self):
        """This should just not throw any exception"""
        container_dwell_time_distribution_seeder.seed()

        for mode_of_transport_i in ModeOfTransport:
            for mode_of_transport_j in ModeOfTransport:
                for storage_requirement in StorageRequirement:
                    entry = ContainerDwellTimeDistribution.select().where(
                        (ContainerDwellTimeDistribution.picked_up_by == mode_of_transport_i)
                        & (ContainerDwellTimeDistribution.delivered_by == mode_of_transport_j)
                        & (ContainerDwellTimeDistribution.storage_requirement == storage_requirement)
                    )
                    self.assertEqual(len(list(entry)), 1)
