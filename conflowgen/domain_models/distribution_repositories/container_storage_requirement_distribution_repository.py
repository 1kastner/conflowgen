import math
from typing import Dict

from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution


class StorageRequirementMissingException(Exception):
    pass


class ContainerLengthMissingException(Exception):
    pass


class SumOfProbabilitiesUnequalOneException(Exception):
    pass


class ContainerStorageRequirementDistributionRepository:
    @staticmethod
    def _validate(distribution: Dict[ContainerLength, Dict[StorageRequirement, float]]):
        if not set(ContainerLength) == set(distribution.keys()):
            raise ContainerLengthMissingException(set(ContainerLength) - set(distribution.keys()))
        for container_length in distribution.keys():
            distribution_for_length = distribution[container_length]
            if not set(StorageRequirement) == set(distribution_for_length.keys()):
                raise StorageRequirementMissingException(set(StorageRequirement) - set(distribution_for_length.keys()))
            sum_of_probabilities = sum(distribution_for_length.values())
            if not math.isclose(sum_of_probabilities, 1):
                raise SumOfProbabilitiesUnequalOneException(sum_of_probabilities)

    @staticmethod
    def _get_fraction(
            container_length: ContainerLength,
            storage_requirement: StorageRequirement
    ) -> float:
        """Loads the fraction of containers."""

        entry = StorageRequirementDistribution.get(
            (StorageRequirementDistribution.container_length == container_length)
            & (StorageRequirementDistribution.storage_requirement == storage_requirement)
        )
        fraction = entry.fraction
        return fraction

    @classmethod
    def get_distribution(cls) -> Dict[ContainerLength, Dict[StorageRequirement, float]]:
        distribution = {
            container_length: {
                storage_requirement: cls._get_fraction(
                    container_length=container_length,
                    storage_requirement=storage_requirement
                )
                for storage_requirement in StorageRequirement
            }
            for container_length in ContainerLength
        }
        cls._validate(distribution)
        return distribution

    def set_distribution(
            self,
            distributions: Dict[ContainerLength, Dict[StorageRequirement, float]]
    ) -> None:
        self._validate(distributions)
        StorageRequirementDistribution.delete().execute()
        for container_length, storage_requirement_distribution in distributions.items():
            for storage_requirement, fraction in storage_requirement_distribution.items():
                StorageRequirementDistribution.create(
                    container_length=container_length,
                    storage_requirement=storage_requirement,
                    fraction=fraction
                ).save()
