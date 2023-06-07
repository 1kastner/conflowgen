import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.api import AbstractDistributionManager
from conflowgen.domain_models.distribution_repositories.container_weight_distribution_repository import \
    ContainerWeightDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength


class ContainerWeightDistributionManager(AbstractDistributionManager):
    """
    This is the interface to set and get the container weight distribution.
    With the help of this distribution, the weight of each container is drawn.
    The default distribution is presented in the section
    `Container Weight Distribution <notebooks/input_distributions.ipynb#Container-Weight-Distribution>`_.
    """

    def __init__(self):
        self.container_weight_repository = ContainerWeightDistributionRepository()

    def get_container_weight_distribution(self) -> typing.Dict[ContainerLength, typing.Dict[int, float]]:
        """
        Returns:
            The distribution of container weights. Each length is assigned its frequency of showing up.
        """
        return self.container_weight_repository.get_distribution()

    def set_container_weight_distribution(
            self,
            container_weights: typing.Dict[ContainerLength, typing.Dict[int, float]]
    ) -> None:
        """
        Set the assumed global distribution of container weights.

        Args:
            container_weights: The distribution of container weights for the respective container lengths.
        """
        sanitized_distribution = self._normalize_and_validate_distribution_with_one_dependent_variable(
            container_weights,
            ContainerLength,
            int,
            values_are_frequencies=True
        )
        self.container_weight_repository.set_distribution(sanitized_distribution)
        DataSummariesCache.reset_cache()
