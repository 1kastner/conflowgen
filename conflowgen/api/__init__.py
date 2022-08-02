import abc
from typing import Dict, Any, Type, TypeVar

from conflowgen.domain_models.distribution_repositories import normalize_distribution_with_no_dependent_variable, \
    normalize_distribution_with_one_dependent_variable, normalize_distribution_with_two_dependent_variables
from conflowgen.domain_models.distribution_validators import validate_distribution_with_no_dependent_variables, \
    validate_distribution_with_one_dependent_variable, validate_distribution_with_two_dependent_variables


class AbstractDistributionManager(abc.ABC):

    KeyEnumFirstLevel = TypeVar('KeyEnumFirstLevel')

    KeyEnumSecondLevel = TypeVar('KeyEnumSecondLevel')

    KeyEnumThirdLevel = TypeVar('KeyEnumThirdLevel')

    @staticmethod
    def _normalize_and_validate_distribution_without_dependent_variables(
            distribution: Dict[Any, float],
            key_type: Type[KeyEnumFirstLevel],
            values_are_frequencies: bool
    ) -> Dict[KeyEnumFirstLevel, float]:
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
            distribution: Dict[Any, Dict[Any, Any]],
            key_type_first_level: Type[KeyEnumFirstLevel],
            key_type_second_level: Type[KeyEnumSecondLevel],
            values_are_frequencies: bool
    ) -> Dict[KeyEnumFirstLevel, Dict[KeyEnumSecondLevel, float]]:
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
            distribution: Dict[Any, Dict[Any, Dict[Any, Any]]],
            key_type_first_level: Type[KeyEnumFirstLevel],
            key_type_second_level: Type[KeyEnumSecondLevel],
            key_type_third_level: Type[KeyEnumThirdLevel],
            values_are_frequencies: bool
    ) -> Dict[KeyEnumFirstLevel, Dict[KeyEnumSecondLevel, Dict[KeyEnumThirdLevel, Any]]]:
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
