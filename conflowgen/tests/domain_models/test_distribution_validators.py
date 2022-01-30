import unittest

from conflowgen import ContainerLength
from conflowgen.domain_models.distribution_validators import DistributionHasNoElementsException, \
    validate_distribution_with_one_dependent_variable, DistributionElementIsMissingException, \
    DistributionProbabilityOutOfRange, DistributionProbabilitiesUnequalOne, \
    validate_distribution_with_no_dependent_variables


class TestDistributionValidatorWithOneDependentVariable(unittest.TestCase):

    def test_validating_completely_empty_distribution_raises_exception(self):
        with self.assertRaises(DistributionHasNoElementsException) as cm:
            validate_distribution_with_one_dependent_variable({})
        expected_message = "The distribution does not have any elements to draw from."
        self.assertEqual(expected_message, str(cm.exception))

    def test_validating_empty_distribution_for_one_dependent_variable_raises_exception(self):
        default_distribution_without_dependent_variable = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionHasNoElementsException) as cm:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: {}  # here is the culprit
            })

        expected_message = (
            'The distribution does not have any elements to draw from. This is error '
            "occurred while examining the dependent variable 'other'.")
        self.assertEqual(expected_message, str(cm.exception))

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
        with self.assertRaises(DistributionElementIsMissingException) as cm:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })

        expected_message = (
            "The distribution {'20 feet': '0.25000', '45 feet': '0.25000', 'other': "
            "'0.25000'} was expected to have the following elements: ['20 feet', '40 "
            "feet', '45 feet', 'other'] but it provided the following elements: ['20 "
            "feet', '45 feet', 'other']. This is error occurred while examining the "
            "dependent variable 'other'."
        )
        self.assertEqual(expected_message, str(cm.exception))

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
        with self.assertRaises(DistributionProbabilityOutOfRange) as cm:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element '40 feet' the probability was -0.25 in the distribution {'20 feet': "
            "'0.25000', '40 feet': '-0.25000', '45 feet': '0.25000', 'other': '0.25000'}. This "
            "is error occurred while examining the dependent variable 'other'.")
        self.assertEqual(expected_message, str(cm.exception))

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
        with self.assertRaises(DistributionProbabilityOutOfRange) as cm:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element '40 feet' the probability was 1.1 in the distribution {'20 feet': "
            "'0.25000', '40 feet': '1.10000', '45 feet': '0.25000', 'other': '0.25000'}. "
            "This is error occurred while examining the dependent variable 'other'.")
        self.assertEqual(expected_message, str(cm.exception))

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
        with self.assertRaises(DistributionProbabilitiesUnequalOne) as cm:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            })

        expected_message = (
            'The sum of all probabilities should sum to 1 but for the '
            "distribution {'20 feet': '0.25000', '40 feet': '1.00000', '45 feet': "
            "'0.25000', 'other': '0.25000'} the sum was 1.75000. This is error occurred "
            "while examining the dependent variable 'other'.")
        self.assertEqual(expected_message, str(cm.exception))


class TestDistributionValidatorWithNoDependentVariables(unittest.TestCase):

    def test_validating_completely_empty_distribution_raises_exception(self):
        with self.assertRaises(DistributionHasNoElementsException) as cm:
            validate_distribution_with_no_dependent_variables({})
        expected_message = 'The distribution does not have any elements to draw from.'
        self.assertEqual(expected_message, str(cm.exception))

    def test_missing_element(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            # ContainerLength.forty_feet is missing
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionElementIsMissingException) as cm:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution
            )

        expected_message = (
            "The distribution {'20 feet': '0.25000', '45 feet': '0.25000', 'other': "
            "'0.25000'} was expected to have the following elements: ['20 feet', '40 "
            "feet', '45 feet', 'other'] but it provided the following elements: ['20 "
            "feet', '45 feet', 'other']."
        )
        self.assertEqual(expected_message, str(cm.exception))

    def test_one_frequency_is_out_of_range_because_it_is_negative(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: -0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionProbabilityOutOfRange) as cm:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution
            )

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element '40 feet' the probability was -0.25 in the distribution {'20 "
            "feet': '0.25000', '40 feet': '-0.25000', '45 feet': '0.25000', 'other': "
            "'0.25000'}."
        )
        self.assertEqual(expected_message, str(cm.exception))

    def test_one_frequency_is_out_of_range_because_it_is_larger_than_one(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 1.1,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionProbabilityOutOfRange) as cm:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution
            )

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element '40 feet' the probability was 1.1 in the distribution {'20 feet': "
            "'0.25000', '40 feet': '1.10000', '45 feet': '0.25000', 'other': '0.25000'}.")
        self.assertEqual(expected_message, str(cm.exception))

    def test_sum_of_frequencies_is_unequal_one(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 1,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionProbabilitiesUnequalOne) as cm:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution
            )

        expected_message = (
            'The sum of all probabilities should sum to 1 but for the '
            "distribution {'20 feet': '0.25000', '40 feet': '1.00000', '45 feet': "
            "'0.25000', 'other': '0.25000'} the sum was 1.75000.")
        self.assertEqual(expected_message, str(cm.exception))
