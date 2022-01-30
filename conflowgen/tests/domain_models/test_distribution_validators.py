import unittest

from conflowgen import ContainerLength
from conflowgen.domain_models.distribution_validators import DistributionHasNoElementsException, \
    validate_distribution_with_one_dependent_variable, DistributionElementIsMissingException, \
    DistributionFrequencyOutOfRange, DistributionProbabilitiesUnequalOne


class TestDistributionValidatorWithOneDependentVariable(unittest.TestCase):

    def test_validating_completely_empty_distribution_raises_exception(self):
        with self.assertRaises(DistributionHasNoElementsException):
            validate_distribution_with_one_dependent_variable({})

    def test_validating_empty_distribution_for_one_dependent_variable_raises_exception(self):
        default_distribution_without_dependent_variable = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionHasNoElementsException):
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: {}
            })

    def test_missing_element_on_second_level(self):
        default_distribution_without_dependent_variable = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            # ContainerLength.forty_feet is missing
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionElementIsMissingException):
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })

    def test_one_frequency_is_out_of_range_because_it_is_negative(self):
        default_distribution_without_dependent_variable = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: -0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionFrequencyOutOfRange):
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })

    def test_one_frequency_is_out_of_range_because_it_is_larger_than_one(self):
        default_distribution_without_dependent_variable = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 1.1,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionFrequencyOutOfRange):
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })

    def test_sum_of_frequencies_is_unequal_one(self):
        default_distribution_without_dependent_variable = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 1,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionProbabilitiesUnequalOne):
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })
