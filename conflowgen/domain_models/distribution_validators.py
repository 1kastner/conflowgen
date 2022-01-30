import math
from typing import Dict, Type, cast, Any, Optional
import enum


class DistributionHasNoElementsException(Exception):
    pass


class DistributionElementIsMissingException(Exception):
    pass


class DistributionFrequencyOutOfRange(Exception):
    pass


class DistributionProbabilitiesUnequalOne(Exception):
    pass


ABSOLUTE_TOLERANCE = 0.05
"""
The absolute tolerance when comparing the sum of all frequencies with 1.
"""


def _check_all_required_keys_are_set_in_distribution(
        distribution: Dict[enum.Enum, Any],
        context: Optional[str] = None
) -> None:
    if len(distribution) == 0:
        msg = "The distribution does not have any elements to draw from."
        if context is not None:
            msg += f" This is error occurred while examining {context}."
        raise DistributionHasNoElementsException(msg)
    provided_elements_in_distribution = list(distribution.keys())
    enum_type_of_first_key = cast(Type[enum.Enum], type(provided_elements_in_distribution[0]))
    theoretically_available_elements = [
        enum_type_of_first_key(el)
        for el in enum_type_of_first_key.__members__.values()
    ]
    if not set(provided_elements_in_distribution) == set(theoretically_available_elements):
        msg = (f"The distribution {_format_distribution(distribution)} was expected to have the following elements: "
               f"{_format_entries(theoretically_available_elements)} but it provided the following elements: "
               f"{_format_entries(provided_elements_in_distribution)}.")
        if context is not None:
            msg += f" This is error occurred while examining {context}."
        raise DistributionElementIsMissingException(msg)


def _check_value_range_of_frequencies_in_distribution(
        distribution: Dict[enum.Enum, float],
        context: Optional[str] = None
) -> None:
    sum_of_frequencies = 0
    for element, frequency in distribution.items():
        if not (0 <= frequency <= 1):
            msg = (
                "The probability of an element to be drawn must range between 0 and 1 "
                f"but for element '{element}' the frequency was {frequency} for the distribution "
                f"{_format_distribution(distribution)}."
            )
            if context is not None:
                msg += f" This is error occurred while examining {context}."
            raise DistributionFrequencyOutOfRange(msg)
        sum_of_frequencies += frequency
    if not math.isclose(sum_of_frequencies, 1, abs_tol=ABSOLUTE_TOLERANCE):
        msg = (
            "The sum of all frequencies/probabilities should sum to 1 "
            f"but for the distribution {_format_distribution(distribution)} the sum was {sum_of_frequencies:.5f}."
        )
        if context is not None:
            msg += f" This is error occurred while examining {context}."
        raise DistributionProbabilitiesUnequalOne(msg)


def validate_distribution_without_dependent_variable(distribution: Dict[enum.Enum, float]) -> None:
    _check_all_required_keys_are_set_in_distribution(distribution)
    _check_value_range_of_frequencies_in_distribution(distribution)


def _format_dependent_variable(dependent_variable: enum.Enum):
    return f"the dependent variable '{dependent_variable}'"


def _format_entry(value: Any):
    if str(value).replace('.', '', 1).isdigit():
        return f"{value:.5f}"
    if isinstance(value, enum.Enum):
        return str(value)
    return "..."


def _format_entries(values: Any) -> str:
    return str([
        _format_entry(value)
        for value in values
    ])


def _format_distribution(distribution: Dict[enum.Enum, Any]) -> str:
    return str(
        {
            str(enum_type_key): _format_entry(value)
            for enum_type_key, value in distribution.items()
        }
    )


def validate_distribution_with_one_dependent_variable(
    distribution: Dict[enum.Enum, Dict[enum.Enum, float]]
) -> None:
    _check_all_required_keys_are_set_in_distribution(distribution)
    for dependent_variable, distribution_of_dependent_variable in distribution.items():
        _check_all_required_keys_are_set_in_distribution(
            distribution_of_dependent_variable, context=_format_dependent_variable(dependent_variable)
        )
        _check_value_range_of_frequencies_in_distribution(
            distribution_of_dependent_variable, context=_format_dependent_variable(dependent_variable)
        )
