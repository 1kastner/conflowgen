import unittest

from conflowgen import ModeOfTransportDistributionManager
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_validators.mode_of_transport_distribution_validator import \
    ModeOfTransportDeliveredWithMissing, ModeOfTransportPickedUpByMissing, ModeOfTransportProportionOutOfRangeException, \
    ModeOfTransportProportionsUnequalOneException
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestModeOfTransportDistributionManager(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ModeOfTransportDistribution
        ])
        mode_of_transport_distribution_seeder.seed()
        self.mode_of_transport_distribution_manager = ModeOfTransportDistributionManager()

    def test_get(self):
        distribution = self.mode_of_transport_distribution_manager.get_mode_of_transport_distributions()
        for delivered_by in ModeOfTransport:
            self.assertIn(delivered_by, distribution.keys())
            for picked_up_by in ModeOfTransport:
                self.assertIn(picked_up_by, distribution[delivered_by].keys())
                mode_of_transport_proportion = distribution[delivered_by][picked_up_by]
                self.assertLessEqual(mode_of_transport_proportion, 1)
                self.assertGreaterEqual(mode_of_transport_proportion, 0)
            sum_of_all_proportions = sum(distribution[delivered_by].values())
            self.assertAlmostEqual(sum_of_all_proportions, 1)

    def test_set_with_missing_keys_first_level(self) -> None:
        with self.assertRaises(ModeOfTransportDeliveredWithMissing):
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distributions(
                {
                    ModeOfTransport.feeder: {
                        ModeOfTransport.train: 0.2,
                        ModeOfTransport.truck: 0.2,
                        ModeOfTransport.barge: 0.2,
                        ModeOfTransport.feeder: 0.2,
                        ModeOfTransport.deep_sea_vessel: 0.2
                    }
                    # other entries missing
                }
            )

    def test_set_with_missing_keys_second_level(self) -> None:
        with self.assertRaises(ModeOfTransportPickedUpByMissing):
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distributions(
                {
                    ModeOfTransport.feeder: {
                        ModeOfTransport.train: 0.2,
                        # other entries missing
                    },
                    ModeOfTransport.truck: {
                        ModeOfTransport.train: 0.2,
                        # other entries missing
                    },
                    ModeOfTransport.barge: {
                        ModeOfTransport.train: 0.2,
                        # other entries missing
                    },
                    ModeOfTransport.deep_sea_vessel: {
                        ModeOfTransport.train: 0.2,
                        # other entries missing
                    },
                    ModeOfTransport.train: {
                        ModeOfTransport.train: 0.2,
                        # other entries missing
                    },
                }
            )

    def test_happy_path(self) -> None:
        self.mode_of_transport_distribution_manager.set_mode_of_transport_distributions(
            {
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
        )

    def test_set_with_wrong_proportions(self) -> None:
        with self.assertRaises(ModeOfTransportProportionOutOfRangeException):
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distributions(
                {
                    ModeOfTransport.feeder: {
                        ModeOfTransport.train: 1.1,  # the malicious entry
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
                })

    def test_set_what_do_not_add_up_to_one(self) -> None:
        with self.assertRaises(ModeOfTransportProportionsUnequalOneException):
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distributions(
                {
                    ModeOfTransport.feeder: {  # these together are beyond 1
                        ModeOfTransport.train: 0.9,
                        ModeOfTransport.truck: 0.9,
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
                })
