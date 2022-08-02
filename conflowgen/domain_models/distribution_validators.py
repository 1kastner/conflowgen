from __future__ import annotations

import copy
import math
from typing import Dict, Type, Any, Optional
import enum


class DistributionHasNoElementsException(Exception):
    pass


class DistributionElementIsMissingException(Exception):
    pass


class DistributionProbabilityOutOfRange(Exception):
    pass


class DistributionProbabilitiesUnequalOne(Exception):
    pass


class DistributionElementIsInvalidException(Exception):
    pass


ABSOLUTE_TOLERANCE = 0.05
"""
The absolute tolerance when comparing the sum of all frequencies with 1.
"""


def _format_dependent_variable(dependent_variable: enum.Enum):
    return f"the dependent variable '{dependent_variable}'"


def _format_entry(value: Any):
    if str(value).replace('.', '', 1).replace('-', '', 1).isdigit():
        return f"{value:.5f}"
    if isinstance(value, enum.Enum):
        return str(value)
    if isinstance(value, dict):
        return "{...}"
    return "..."


def _format_entries(values: Any) -> str:
    return str([
        _format_entry(value)
        for value in values
    ])


def _format_distribution(distribution: Dict[enum.Enum, Any]) -> str:
    entries = []
    for enum_type_key, value in distribution.items():
        entry = repr(str(enum_type_key)) + ": " + _format_entry(value)
        entries.append(entry)
    text = "{"
    text += ", ".join(entries)
    text += "}"
    return text


def _cast_element_type(actual_element: Any, desired_element_type: Type[enum.Enum]) -> enum.Enum | None:
    """
    Args:
        actual_element: The key the user provided
        desired_element_type: The required element type

    Returns:
        Is the actual element of the desired element type?
    """
    if isinstance(actual_element, desired_element_type):
        return actual_element  # no casting required
    try:  # check if it is a valid value
        return desired_element_type(actual_element)
    except ValueError:
        pass
    try:  # check if it is a valid name
        return desired_element_type[actual_element]
    except KeyError:
        pass
    if hasattr(desired_element_type, "cast_element_type"):  # use enum custom code if available
        return desired_element_type.cast_element_type(actual_element)
    return None


def _check_all_required_keys_of_enum_are_set_in_distribution(
        distribution: Dict[enum.Enum, Any],
        desired_element_type: Type[enum.Enum],
        context: Optional[str] = None
):
    sanitized_distribution = copy.deepcopy(distribution)
    provided_elements_in_distribution = list(distribution.keys())
    for element in provided_elements_in_distribution:
        casted_element = _cast_element_type(element, desired_element_type)
        if casted_element is None:
            raise DistributionElementIsInvalidException(
                f"Element '{element}' could not be casted to type '{desired_element_type}'"
            )
        if casted_element != element:
            sanitized_distribution[casted_element] = sanitized_distribution.pop(element)  # update key
    theoretically_available_elements = [
        desired_element_type(el)
        for el in desired_element_type.__members__.values()
    ]
    if not set(sanitized_distribution.keys()) == set(theoretically_available_elements):
        msg = (f"The distribution {_format_distribution(distribution)} was expected to have the following elements: "
               f"{_format_entries(theoretically_available_elements)} but it provided the following elements: "
               f"{_format_entries(provided_elements_in_distribution)}.")
        if context is not None:
            msg += f" This is error occurred while examining {context}."
        raise DistributionElementIsMissingException(msg)
    return sanitized_distribution


def _check_all_keys_are_of_intended_primitive_type(
        distribution: Dict[enum.Enum, Any],
        desired_element_type: Any
):
    sanitized_distribution = copy.deepcopy(distribution)
    provided_elements_in_distribution = list(distribution.keys())
    for element in provided_elements_in_distribution:
        try:
            casted_element = desired_element_type(element)
        except ValueError as exception:
            raise DistributionElementIsInvalidException(
                f"Element '{element}' could not be casted to type '{desired_element_type}'"
            ) from exception
        if casted_element != element:
            sanitized_distribution[casted_element] = sanitized_distribution.pop(element)  # update key
    return sanitized_distribution


SUPPORTED_PRIMITIVE_KEY_TYPES = (int, )


def _check_all_required_keys_are_set_in_distribution(
        distribution: Dict[enum.Enum, Any],
        desired_element_type: Type[enum.Enum] | int,
        context: Optional[str] = None
) -> Dict[enum.Enum | int, Any]:

    if len(distribution) == 0:
        msg = "The distribution does not have any elements to draw from."
        if context is not None:
            msg += f" This is error occurred while examining {context}."
        raise DistributionHasNoElementsException(msg)

    if desired_element_type in SUPPORTED_PRIMITIVE_KEY_TYPES:
        # This is a primitive and for such no obligatory value lists exist.
        # This is the case e.g. for container weights.
        sanitized_distribution = _check_all_keys_are_of_intended_primitive_type(
            distribution,
            desired_element_type
        )
    else:
        sanitized_distribution = _check_all_required_keys_of_enum_are_set_in_distribution(
            distribution,
            desired_element_type,
            context
        )
    return sanitized_distribution


def _check_value_range_of_frequencies_in_distribution(
        distribution: Dict[enum.Enum, Any],
        context: Optional[str] = None
) -> None:
    sum_of_probabilities = 0
    for element, probability in distribution.items():
        if not (0 <= probability <= 1):
            msg = (
                "The probability of an element to be drawn must range between 0 and 1 "
                f"but for the element '{element}' the probability was {probability} in the distribution "
                f"{_format_distribution(distribution)}."
            )
            if context is not None:
                msg += f" This is error occurred while examining {context}."
            raise DistributionProbabilityOutOfRange(msg)
        sum_of_probabilities += probability
    if not math.isclose(sum_of_probabilities, 1, abs_tol=ABSOLUTE_TOLERANCE):
        msg = (
            "The sum of all probabilities should sum to 1 "
            f"but for the distribution {_format_distribution(distribution)} the sum was {sum_of_probabilities:.5f}."
        )
        if context is not None:
            msg += f" This is error occurred while examining {context}."
        raise DistributionProbabilitiesUnequalOne(msg)


def validate_distribution_with_no_dependent_variables(
        distribution: Dict[enum.Enum | int, Any],
        key_type: Type[enum.Enum] | Type[int],
        values_are_frequencies: bool
) -> Dict[enum.Enum | int, float]:
    sanitized_distribution = _check_all_required_keys_are_set_in_distribution(distribution, key_type)
    if values_are_frequencies:
        _check_value_range_of_frequencies_in_distribution(sanitized_distribution)
    return sanitized_distribution


def validate_distribution_with_one_dependent_variable(
        distribution: Dict[enum.Enum, Dict[enum.Enum | int, Any]],
        key_type_of_independent_variable: Type[enum.Enum],
        key_type_of_dependent_variable: Type[enum.Enum] | Type[int],
        values_are_frequencies: bool
) -> Dict[enum.Enum, Dict[enum.Enum | int, Any]]:
    sanitized_distribution = _check_all_required_keys_are_set_in_distribution(
        distribution, key_type_of_independent_variable
    )
    for dependent_variable, distribution_of_dependent_variable in sanitized_distribution.items():
        sanitized_distribution_of_dependent_variable = _check_all_required_keys_are_set_in_distribution(
            distribution_of_dependent_variable,
            key_type_of_dependent_variable,
            context=_format_dependent_variable(dependent_variable)
        )
        if values_are_frequencies:
            _check_value_range_of_frequencies_in_distribution(
                sanitized_distribution_of_dependent_variable,
                context=_format_dependent_variable(dependent_variable)
            )
        sanitized_distribution[dependent_variable] = sanitized_distribution_of_dependent_variable
    return sanitized_distribution


def validate_distribution_with_two_dependent_variables(
        distribution: Dict[enum.Enum, Dict[enum.Enum, Dict[enum.Enum | int, Any]]],
        key_type_of_independent_variable: Type[enum.Enum],
        key_type_of_first_dependent_variable: Type[enum.Enum] | Type[int],
        key_type_of_second_dependent_variable: Type[enum.Enum] | Type[int],
        values_are_frequencies: bool
) -> Dict[enum.Enum, Dict[enum.Enum, Dict[enum.Enum | int, Any]]]:
    sanitized_top_level_distribution = _check_all_required_keys_are_set_in_distribution(
        distribution, key_type_of_independent_variable
    )
    for first_dependent_variable, distribution_of_first_dependent_variable in sanitized_top_level_distribution.items():
        sanitized_distribution_of_first_dependent_variable = _check_all_required_keys_are_set_in_distribution(
            distribution_of_first_dependent_variable,
            key_type_of_first_dependent_variable,
            context=_format_dependent_variable(first_dependent_variable)
        )
        sanitized_top_level_distribution[first_dependent_variable] = sanitized_distribution_of_first_dependent_variable

        for second_dependent_variable, distribution_of_second_dependent_variable in \
                sanitized_distribution_of_first_dependent_variable.items():
            sanitized_distribution_of_second_dependent_variable = _check_all_required_keys_are_set_in_distribution(
                distribution_of_second_dependent_variable,
                key_type_of_second_dependent_variable,
                context=_format_dependent_variable(second_dependent_variable)
            )
            if values_are_frequencies:
                _check_value_range_of_frequencies_in_distribution(
                    sanitized_distribution_of_second_dependent_variable,
                    context=_format_dependent_variable(second_dependent_variable)
                )
            sanitized_top_level_distribution[first_dependent_variable][second_dependent_variable] = \
                sanitized_distribution_of_second_dependent_variable

    return sanitized_top_level_distribution
