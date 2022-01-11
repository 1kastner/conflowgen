from typing import Dict

from conflowgen.domain_models.distribution_repositories.container_weight_distribution_repository import \
    ContainerWeightDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength


class ContainerWeightDistributionManager:
    """
    This manager provides the interface to set and get the container weight distribution.
    """

    def __init__(self):
        self.container_weight_repository = ContainerWeightDistributionRepository()

    def get_container_weights(self) -> Dict[ContainerLength, Dict[int, float]]:
        """
        Returns: The distribution of container lengths. Each length is assigned its frequency of showing up.
        """
        return self.container_weight_repository.get_distribution()

    def set_container_weights(
            self,
            container_lengths: Dict[ContainerLength, Dict[int, float]]
    ) -> None:
        """
        Set the assumed global distribution of container lengths. This is applied to all vehicles that arrive at the
        terminal.

        Args:
            container_lengths: The distribution of container lengths and their corresponding frequency.
        """
        self.container_weight_repository.set_distribution(container_lengths)
