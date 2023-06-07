import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.api import AbstractDistributionManager
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.distribution_repositories.storage_requirement_distribution_repository import \
    StorageRequirementDistributionRepository


class StorageRequirementDistributionManager(AbstractDistributionManager):
    """
    This is the interface to set and get the storage requirement distribution.
    It determines how many containers are selected to have a certain :class:`.StorageRequirement`.
    """

    def __init__(self):
        self.storage_requirement_repository = StorageRequirementDistributionRepository()

    def get_storage_requirement_distribution(
            self
    ) -> typing.Dict[ContainerLength, typing.Dict[StorageRequirement, float]]:
        """
        Returns:
            The distribution of storage requirements based on the length of the container.
        """
        return self.storage_requirement_repository.get_distribution()

    def set_storage_requirement_distribution(
            self,
            storage_requirements: typing.Dict[ContainerLength, typing.Dict[StorageRequirement, float]]
    ) -> None:
        """
        Set the assumed global distribution of container storage requirements.
        This is applied to all containers passing through the terminal.

        Args:
            storage_requirements: The distribution of storage requirements depending on the container length.
        """
        sanitized_distribution = self._normalize_and_validate_distribution_with_one_dependent_variable(
            storage_requirements,
            ContainerLength,
            StorageRequirement,
            values_are_frequencies=True
        )
        self.storage_requirement_repository.set_distribution(sanitized_distribution)
        DataSummariesCache.reset_cache()
