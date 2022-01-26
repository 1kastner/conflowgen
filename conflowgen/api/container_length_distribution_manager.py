from typing import Dict

from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength


class ContainerLengthDistributionManager:
    """
    This manager provides the interface to set and get the container length distribution.

    The default distribution is presented in the section
    `Container Length Distribution <notebooks/input_distributions.ipynb#Container-Length-Distribution>`_.
    """

    def __init__(self):
        self.container_length_repository = ContainerLengthDistributionRepository()

    def get_container_length_distribution(self) -> Dict[ContainerLength, float]:
        """
        Returns: The distribution of container lengths. Each length is assigned its frequency of showing up.
        """
        return self.container_length_repository.get_distribution()

    def set_container_length_distribution(
            self,
            container_lengths: Dict[ContainerLength, float]
    ) -> None:
        """
        Set the assumed global distribution of container lengths. This is applied to all vehicles that arrive at the
        terminal.

        Args:
            container_lengths: The distribution of container lengths and their corresponding frequency.
        """
        self.container_length_repository.set_distribution(container_lengths)
