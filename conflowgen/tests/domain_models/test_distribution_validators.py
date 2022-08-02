import unittest

from conflowgen import ContainerLength, StorageRequirement
from conflowgen.domain_models.distribution_validators import DistributionHasNoElementsException, \
    validate_distribution_with_one_dependent_variable, DistributionElementIsMissingException, \
    DistributionProbabilityOutOfRange, DistributionProbabilitiesUnequalOne, \
    validate_distribution_with_no_dependent_variables, DistributionElementIsInvalidException


class TestDistributionValidatorWithOneDependentVariable(unittest.TestCase):

    def test_validating_completely_empty_distribution_raises_exception(self):
        with self.assertRaises(DistributionHasNoElementsException) as context:
            validate_distribution_with_one_dependent_variable(
                {}, ContainerLength, StorageRequirement, values_are_frequencies=True
            )
        expected_message = "The distribution does not have any elements to draw from."
        self.assertEqual(expected_message, str(context.exception))

    def test_validating_empty_distribution_for_one_dependent_variable_raises_exception(self):
        default_distribution_without_dependent_variable = {
            StorageRequirement.reefer: 0.25,
            StorageRequirement.standard: 0.25,
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        with self.assertRaises(DistributionHasNoElementsException) as context:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: {}  # here is the culprit
            }, ContainerLength, StorageRequirement, values_are_frequencies=True)

        expected_message = (
            'The distribution does not have any elements to draw from. This is error '
            "occurred while examining the dependent variable 'other'.")
        self.assertEqual(expected_message, str(context.exception))

    def test_missing_element_on_second_level(self):
        default_distribution_without_dependent_variable = {
            StorageRequirement.reefer: 0.25,
            StorageRequirement.standard: 0.25,
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        variation_of_distribution = {
            StorageRequirement.reefer: 0.25,
            # StorageRequirement.standard is missing
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        with self.assertRaises(DistributionElementIsMissingException) as context:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            }, ContainerLength, StorageRequirement, values_are_frequencies=True)

        expected_message = (
            "The distribution {'reefer': 0.25000, 'empty': 0.25000, 'dangerous_goods': "
            "0.25000} was expected to have the following elements: ['empty', 'standard', "
            "'reefer', 'dangerous_goods'] but it provided the following elements: "
            "['reefer', 'empty', 'dangerous_goods']. This is error occurred while "
            "examining the dependent variable 'other'.")
        self.assertEqual(expected_message, str(context.exception))

    def test_one_frequency_is_out_of_range_because_it_is_negative(self):
        default_distribution_without_dependent_variable = {
            StorageRequirement.reefer: 0.25,
            StorageRequirement.standard: 0.25,
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        variation_of_distribution = {
            StorageRequirement.reefer: 0.25,
            StorageRequirement.standard: -0.25,
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        with self.assertRaises(DistributionProbabilityOutOfRange) as context:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            }, ContainerLength, StorageRequirement, values_are_frequencies=True)

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element 'standard' the probability was -0.25 in the distribution "
            "{'reefer': 0.25000, 'standard': -0.25000, 'empty': 0.25000, "
            "'dangerous_goods': 0.25000}. This is error occurred while examining the "
            "dependent variable 'other'.")
        self.assertEqual(expected_message, str(context.exception))

    def test_element_is_invalid(self):
        default_distribution_without_dependent_variable = {
            StorageRequirement.reefer: 0.25,
            StorageRequirement.standard: 0.25,
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        variation_of_distribution = {
            StorageRequirement.reefer: 0.25,
            ContainerLength.forty_feet: 0.25,  # the culprit
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        with self.assertRaises(DistributionElementIsInvalidException) as context:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            }, ContainerLength, StorageRequirement, values_are_frequencies=True)

        expected_message = "Element '40 feet' could not be casted to type '<enum 'StorageRequirement'>'"
        self.assertEqual(expected_message, str(context.exception))

    def test_one_frequency_is_out_of_range_because_it_is_larger_than_one(self):
        default_distribution_without_dependent_variable = {
            StorageRequirement.reefer: 0.25,
            StorageRequirement.standard: 0.25,
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        variation_of_distribution = {
            StorageRequirement.reefer: 0.25,
            StorageRequirement.standard: 1.1,
            StorageRequirement.empty: 0.25,
            StorageRequirement.dangerous_goods: 0.25
        }
        with self.assertRaises(DistributionProbabilityOutOfRange) as context:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            }, ContainerLength, StorageRequirement, values_are_frequencies=True)

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element 'standard' the probability was 1.1 in the distribution "
            "{'reefer': 0.25000, 'standard': 1.10000, 'empty': 0.25000, "
            "'dangerous_goods': 0.25000}. This is error occurred while examining the "
            "dependent variable 'other'.")
        self.assertEqual(expected_message, str(context.exception))

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
        with self.assertRaises(DistributionProbabilitiesUnequalOne) as context:
            validate_distribution_with_one_dependent_variable({
                ContainerLength.twenty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_feet: default_distribution_without_dependent_variable,
                ContainerLength.forty_five_feet: default_distribution_without_dependent_variable,
                ContainerLength.other: variation_of_distribution
            }, ContainerLength, ContainerLength, values_are_frequencies=True)

        expected_message = (
            'The sum of all probabilities should sum to 1 but for the '
            "distribution {'20 feet': 0.25000, '40 feet': 1.00000, '45 feet': "
            "0.25000, 'other': 0.25000} the sum was 1.75000. This is error occurred "
            "while examining the dependent variable 'other'.")
        self.assertEqual(expected_message, str(context.exception))

    def test_distribution_with_ints_on_second_level(self):
        distribution_with_int_keys = {
            ContainerLength.twenty_feet: {
                10: 0.2,
                20: 0.5,
                30: 0.3,
            },
            ContainerLength.forty_feet: {
                10: 0.2,
                20: 0.5,
                30: 0.3,
            },
            ContainerLength.forty_five_feet: {
                10: 0.2,
                20: 0.5,
                30: 0.3,
            },
            ContainerLength.other: {
                10: 0.2,
                20: 0.5,
                30: 0.3,
            }
        }
        sanitized_distribution = validate_distribution_with_one_dependent_variable(
            distribution_with_int_keys,
            ContainerLength,
            int,
            True
        )

        self.assertDictEqual(distribution_with_int_keys, sanitized_distribution)


class TestDistributionValidatorWithNoDependentVariables(unittest.TestCase):

    def test_validating_completely_empty_distribution_raises_exception(self):
        with self.assertRaises(DistributionHasNoElementsException) as context:
            validate_distribution_with_no_dependent_variables({}, ContainerLength, values_are_frequencies=True)
        expected_message = 'The distribution does not have any elements to draw from.'
        self.assertEqual(expected_message, str(context.exception))

    def test_missing_element(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            # ContainerLength.forty_feet is missing
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionElementIsMissingException) as context:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution, ContainerLength, values_are_frequencies=True
            )

        expected_message = (
            "The distribution {'20 feet': 0.25000, '45 feet': 0.25000, 'other': "
            "0.25000} was expected to have the following elements: ['20 feet', '40 "
            "feet', '45 feet', 'other'] but it provided the following elements: ['20 "
            "feet', '45 feet', 'other']."
        )
        self.assertEqual(expected_message, str(context.exception))

    def test_one_frequency_is_out_of_range_because_it_is_negative(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: -0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionProbabilityOutOfRange) as context:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution, ContainerLength, values_are_frequencies=True
            )

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element '40 feet' the probability was -0.25 in the distribution {'20 "
            "feet': 0.25000, '40 feet': -0.25000, '45 feet': 0.25000, 'other': "
            "0.25000}."
        )
        self.assertEqual(expected_message, str(context.exception))

    def test_one_frequency_is_out_of_range_because_it_is_larger_than_one(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 1.1,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionProbabilityOutOfRange) as context:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution, ContainerLength, values_are_frequencies=True
            )

        expected_message = (
            'The probability of an element to be drawn must range between 0 and 1 but for '
            "the element '40 feet' the probability was 1.1 in the distribution {'20 feet': "
            "0.25000, '40 feet': 1.10000, '45 feet': 0.25000, 'other': 0.25000}.")
        self.assertEqual(expected_message, str(context.exception))

    def test_sum_of_frequencies_is_unequal_one(self):
        variation_of_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 1,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        with self.assertRaises(DistributionProbabilitiesUnequalOne) as context:
            validate_distribution_with_no_dependent_variables(
                variation_of_distribution, ContainerLength, values_are_frequencies=True
            )

        expected_message = (
            'The sum of all probabilities should sum to 1 but for the '
            "distribution {'20 feet': 0.25000, '40 feet': 1.00000, '45 feet': "
            "0.25000, 'other': 0.25000} the sum was 1.75000.")
        self.assertEqual(expected_message, str(context.exception))

    def test_auto_cast(self):
        dirty_distribution = {
            '20 feet': 0.25,
            40: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            -1: 0.25
        }
        clean_distribution = {
            ContainerLength.twenty_feet: 0.25,
            ContainerLength.forty_feet: 0.25,
            ContainerLength.forty_five_feet: 0.25,
            ContainerLength.other: 0.25
        }
        sanitized_distribution = validate_distribution_with_no_dependent_variables(
            dirty_distribution, ContainerLength, values_are_frequencies=True
        )
        self.assertDictEqual(clean_distribution, sanitized_distribution)

    def test_distribution_with_ints(self):
        distribution_with_int_keys = {
            10: 0.2,
            20: 0.5,
            30: 0.3,
        }
        sanitized_distribution = validate_distribution_with_no_dependent_variables(
            distribution_with_int_keys,
            int,
            values_are_frequencies=True
        )

        self.assertDictEqual(distribution_with_int_keys, sanitized_distribution)
