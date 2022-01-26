from typing import Dict

from conflowgen.domain_models.distribution_repositories import normalize_nested_distribution
from conflowgen.domain_models.distribution_repositories.container_weight_distribution_repository import \
    ContainerWeightDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength


class ContainerWeightDistributionManager:
    """
    This manager provides the interface to set and get the container weight distribution.

    The default distribution is presented in the section
    `Container Weight Distribution <notebooks/input_distributions.ipynb#Container-Weight-Distribution>`_.
    """

    def __init__(self):
        self.container_weight_repository = ContainerWeightDistributionRepository()

    def get_container_weight_distribution(self) -> Dict[ContainerLength, Dict[int, float]]:
        """
        Returns:
            The distribution of container weights. Each length is assigned its frequency of showing up.
        """
        return self.container_weight_repository.get_distribution()

    def set_container_weight_distribution(
            self,
            container_weights: Dict[ContainerLength, Dict[int, float]]
    ) -> None:
        """
        Set the assumed global distribution of container weights.

        Args:
            container_weights: The distribution of container weights for the respective container lengths.
        """
        normalized_container_weights = normalize_nested_distribution(container_weights)
        self.container_weight_repository.set_distribution(normalized_container_weights)
