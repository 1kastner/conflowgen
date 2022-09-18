import abc
import typing

from conflowgen.domain_models.distribution_repositories import normalize_distribution_with_no_dependent_variable, \
    normalize_distribution_with_one_dependent_variable, normalize_distribution_with_two_dependent_variables
from conflowgen.domain_models.distribution_validators import validate_distribution_with_no_dependent_variables, \
    validate_distribution_with_one_dependent_variable, validate_distribution_with_two_dependent_variables


class AbstractDistributionManager(abc.ABC):

    KeyEnumFirstLevel = typing.TypeVar('KeyEnumFirstLevel')

    KeyEnumSecondLevel = typing.TypeVar('KeyEnumSecondLevel')

    KeyEnumThirdLevel = typing.TypeVar('KeyEnumThirdLevel')

    @staticmethod
    def _normalize_and_validate_distribution_without_dependent_variables(
            distribution: typing.Dict[typing.Any, float],
            key_type: typing.Type[KeyEnumFirstLevel],
            values_are_frequencies: bool
    ) -> typing.Dict[KeyEnumFirstLevel, float]:
        normalized_distribution = normalize_distribution_with_no_dependent_variable(
            distribution,
            values_are_frequencies=values_are_frequencies
        )
        validated_distribution = validate_distribution_with_no_dependent_variables(
            normalized_distribution,
            key_type,
            values_are_frequencies=True
        )
        return validated_distribution

    @staticmethod
    def _normalize_and_validate_distribution_with_one_dependent_variable(
            distribution: typing.Dict[typing.Any, typing.Dict[typing.Any, typing.Any]],
            key_type_first_level: typing.Type[KeyEnumFirstLevel],
            key_type_second_level: typing.Type[KeyEnumSecondLevel],
            values_are_frequencies: bool
    ) -> typing.Dict[KeyEnumFirstLevel, typing.Dict[KeyEnumSecondLevel, float]]:
        normalized_distribution = normalize_distribution_with_one_dependent_variable(
            distribution,
            values_are_frequencies=values_are_frequencies
        )
        validated_distribution = validate_distribution_with_one_dependent_variable(
            normalized_distribution,
            key_type_first_level,
            key_type_second_level,
            values_are_frequencies
        )
        return validated_distribution

    @staticmethod
    def _normalize_and_validate_distribution_with_two_dependent_variables(
            distribution: typing.Dict[typing.Any, typing.Dict[typing.Any, typing.Dict[typing.Any, typing.Any]]],
            key_type_first_level: typing.Type[KeyEnumFirstLevel],
            key_type_second_level: typing.Type[KeyEnumSecondLevel],
            key_type_third_level: typing.Type[KeyEnumThirdLevel],
            values_are_frequencies: bool
    ) -> typing.Dict[KeyEnumFirstLevel, typing.Dict[KeyEnumSecondLevel, typing.Dict[KeyEnumThirdLevel, typing.Any]]]:
        normalized_distribution = normalize_distribution_with_two_dependent_variables(
            distribution,
            values_are_frequencies=False
        )
        validated_distribution = validate_distribution_with_two_dependent_variables(
            normalized_distribution,
            key_type_first_level,
            key_type_second_level,
            key_type_third_level,
            values_are_frequencies=values_are_frequencies
        )
        return validated_distribution
