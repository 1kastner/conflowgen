import unittest

from conflowgen import ModeOfTransportDistributionManager, ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.distribution_validators import DistributionElementIsMissingException, \
    DistributionElementIsInvalidException, validate_distribution_with_one_dependent_variable
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
        with self.assertRaises(DistributionElementIsMissingException) as context:
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
            "The distribution {'feeder': {...}} was expected to have the following "
            "elements: ['truck', 'train', 'feeder', 'deep_sea_vessel', 'barge'] but it "
            "provided the following elements: ['feeder'].")
        self.assertEqual(expected_message, str(context.exception))

    def test_set_with_missing_keys_second_level(self) -> None:
        with self.assertRaises(DistributionElementIsMissingException) as context:
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
            "The distribution {'train': 1.00000} was expected to have the following "
            "elements: ['truck', 'train', 'feeder', 'deep_sea_vessel', 'barge'] but it "
            "provided the following elements: ['train']. This is error occurred while "
            "examining the dependent variable 'feeder'."
        )
        self.assertEqual(expected_message, str(context.exception))

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

    def test_set_distribution_with_wrongly_typed_distribution(self) -> None:
        with self.assertRaises(DistributionElementIsInvalidException) as context:
            self.mode_of_transport_distribution_manager.set_mode_of_transport_distribution(
                {
                    ContainerLength.twenty_feet: {  # the culprit
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
                })
        expected_message = "Element '20 feet' could not be casted to type '<enum 'ModeOfTransport'>'"
        self.assertEqual(expected_message, str(context.exception))

    def test_set_distribution_with_dirty_distribution(self) -> None:
        clean_distribution = {
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

        dirty_distribution = {
            "feeder": {
                ModeOfTransport.train: 0.2,
                ModeOfTransport.truck: 0.2,
                "barge": 0.2,
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
        sanitized_distribution = validate_distribution_with_one_dependent_variable(
            dirty_distribution, ModeOfTransport, ModeOfTransport, values_are_frequencies=True
        )
        self.assertDictEqual(sanitized_distribution, clean_distribution)
