from typing import Dict

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.distribution_repositories.container_storage_requirement_distribution_repository import \
    ContainerStorageRequirementDistributionRepository


class ContainerStorageRequirementDistributionManager:
    """
    This manager provides the interface to set and get the storage requirement distribution.
    """

    def __init__(self):
        self.storage_requirement_repository = ContainerStorageRequirementDistributionRepository()

    def get_storage_requirements(self) -> Dict[ContainerLength, Dict[StorageRequirement, float]]:
        """
        Returns: The distribution of storage requirements based on the length of the container.
        """
        return self.storage_requirement_repository.get_distribution()

    def set_storage_requirements(
            self,
            storage_requirements: Dict[ContainerLength, Dict[StorageRequirement, float]]
    ) -> None:
        """
        Set the assumed global distribution of container storage requirements. This is applied to all vehicles that
        arrive at the terminal.

        Args:
            storage_requirements: The distribution of storage requirements depending on the container length.
        """
        self.storage_requirement_repository.set_distribution(storage_requirements)
