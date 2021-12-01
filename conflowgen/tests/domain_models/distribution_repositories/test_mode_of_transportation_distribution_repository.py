import unittest

from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestModeOfTransportationDistributionRepository(unittest.TestCase):
    default_data = {
        ModeOfTransport.feeder: {
            ModeOfTransport.train: 0.2,
            ModeOfTransport.truck: 0.2,
            ModeOfTransport.barge: 0.2,
            ModeOfTransport.feeder: 0.2,
            ModeOfTransport.deep_sea_vessel: 0.2
        },
        ModeOfTransport.truck: {
            ModeOfTransport.train: 0.2,
            ModeOfTransport.truck: 0.2,
            ModeOfTransport.barge: 0.2,
            ModeOfTransport.feeder: 0.2,
            ModeOfTransport.deep_sea_vessel: 0.2
        },
        ModeOfTransport.barge: {
            ModeOfTransport.train: 0.2,
            ModeOfTransport.truck: 0.2,
            ModeOfTransport.barge: 0.2,
            ModeOfTransport.feeder: 0.2,
            ModeOfTransport.deep_sea_vessel: 0.2
        },
        ModeOfTransport.deep_sea_vessel: {
            ModeOfTransport.train: 0.2,
            ModeOfTransport.truck: 0.2,
            ModeOfTransport.barge: 0.2,
            ModeOfTransport.feeder: 0.2,
            ModeOfTransport.deep_sea_vessel: 0.2
        },
        ModeOfTransport.train: {
            ModeOfTransport.train: 0.2,
            ModeOfTransport.truck: 0.2,
            ModeOfTransport.barge: 0.2,
            ModeOfTransport.feeder: 0.2,
            ModeOfTransport.deep_sea_vessel: 0.2
        }
    }

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ModeOfTransportDistribution
        ])
        mode_of_transport_distribution_seeder.seed()

    def test_that_distribution_is_n_to_n(self):
        for mode_of_transport in ModeOfTransport:
            picked_up_by_entries = ModeOfTransportDistribution.select().where(
                ModeOfTransportDistribution.picked_up_by == mode_of_transport
            )
            self.assertEqual(len(list(picked_up_by_entries)), len(ModeOfTransport))
        for mode_of_transport_i in ModeOfTransport:
            for mode_of_transport_j in ModeOfTransport:
                entry = ModeOfTransportDistribution.select().where(
                    (ModeOfTransportDistribution.picked_up_by == mode_of_transport_i)
                    & (ModeOfTransportDistribution.delivered_by == mode_of_transport_j)
                )
                self.assertEqual(len(list(entry)), 1)

    def test_distribution_loader(self):
        mode_of_transport_distribution = ModeOfTransportDistributionRepository.get_distribution()

        for mode_of_transport in ModeOfTransport:
            distribution_for_mode_of_transport = sum(mode_of_transport_distribution[mode_of_transport].values())
            self.assertAlmostEqual(
                distribution_for_mode_of_transport,
                1,
                msg=f"All probabilities must sum to 1, but you only achieved {distribution_for_mode_of_transport}"
            )

    def test_happy_path(self):
        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions(
            self.default_data
        )

    def test_set_twice(self):
        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions(
            self.default_data
        )
        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions(
            self.default_data
        )
