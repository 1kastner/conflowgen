import abc
from typing import Dict, Any, Type, TypeVar

from conflowgen.domain_models.distribution_repositories import normalize_distribution_with_no_dependent_variable, \
    normalize_distribution_with_one_dependent_variable
from conflowgen.domain_models.distribution_validators import validate_distribution_with_no_dependent_variables, \
    validate_distribution_with_one_dependent_variable


class AbstractDistributionManager(abc.ABC):

    KeyEnumFirstLevel = TypeVar('KeyEnumFirstLevel')

    KeyEnumSecondLevel = TypeVar('KeyEnumSecondLevel')

    @staticmethod
    def _normalize_and_validate_distribution_without_dependent_variables(
            distribution: Dict[Any, float],
            key_type: Type[KeyEnumFirstLevel]
    ) -> Dict[KeyEnumFirstLevel, float]:
        normalized_distribution = normalize_distribution_with_no_dependent_variable(distribution)
        validated_distribution = validate_distribution_with_no_dependent_variables(
            normalized_distribution,
            key_type
        )
        return validated_distribution

    @staticmethod
    def _normalize_and_validate_distribution_with_one_dependent_variable(
            distribution: Dict[Any, Dict[Any, float]],
            key_type_first_level: Type[KeyEnumFirstLevel],
            key_type_second_level: Type[KeyEnumSecondLevel]
    ) -> Dict[KeyEnumFirstLevel, Dict[KeyEnumSecondLevel, float]]:
        normalized_distribution = normalize_distribution_with_one_dependent_variable(distribution)
        validated_distribution = validate_distribution_with_one_dependent_variable(
            normalized_distribution,
            key_type_first_level,
            key_type_second_level
        )
        return validated_distribution
