import unittest

from conflowgen import ModeOfTransportDistributionManager
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.distribution_validators import DistributionProbabilitiesUnequalOne, \
    DistributionProbabilityOutOfRange, DistributionElementIsMissingException
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
        distribution = self.mode_of_transport_distribution_manager.get_mode_of_transport_distribution()
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
        with self.assertRaises(DistributionElementIsMissingException) as cm:
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distribution(
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

        expected_message = (
            "The distribution {'feeder': '...'} was expected to have the following "
            "elements: ['truck', 'train', 'feeder', 'deep_sea_vessel', 'barge'] but it "
            "provided the following elements: ['feeder'].")
        self.assertEqual(expected_message, str(cm.exception))

    def test_set_with_missing_keys_second_level(self) -> None:
        with self.assertRaises(DistributionElementIsMissingException) as cm:
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distribution(
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
        expected_message = (
            "The distribution {'train': '0.20000'} was expected to have the following "
            "elements: ['truck', 'train', 'feeder', 'deep_sea_vessel', 'barge'] but it "
            "provided the following elements: ['train']. This is error occurred while "
            "examining the dependent variable 'feeder'."
        )
        self.assertEqual(expected_message, str(cm.exception))

    def test_happy_path(self) -> None:
        self.mode_of_transport_distribution_manager.set_mode_of_transport_distribution(
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
        with self.assertRaises(DistributionProbabilityOutOfRange) as cm:
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distribution(
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
        expected_exception_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element 'train' the probability was 1.1 in the distribution {'train': "
            "'1.10000', 'truck': '0.20000', 'barge': '0.20000', 'feeder': '0.20000', "
            "'deep_sea_vessel': '0.20000'}. This is error occurred while examining the "
            "dependent variable 'feeder'.")
        self.assertEqual(expected_exception_message, str(cm.exception))

    def test_set_distribution_that_does_not_add_up_to_one(self) -> None:
        with self.assertRaises(DistributionProbabilitiesUnequalOne) as cm:
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distribution(
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
        expected_message = (
            'The sum of all probabilities should sum to 1 but for the '
            "distribution {'train': '0.90000', 'truck': '0.90000', 'barge': '0.20000', "
            "'feeder': '0.20000', 'deep_sea_vessel': '0.20000'} the sum was 2.40000. This "
            "is error occurred while examining the dependent variable 'feeder'."
        )
        self.assertEqual(expected_message, str(cm.exception))
