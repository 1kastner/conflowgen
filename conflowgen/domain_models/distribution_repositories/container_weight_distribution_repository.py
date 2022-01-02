from typing import Dict

from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.data_types.container_length import ContainerLength


class MissingContainerWeightDistributionEntryException(Exception):
    pass


class ContainerWeightDistributionRepository:

    @staticmethod
    def _get_fraction_for_container_type(
            container_length: ContainerLength,
            container_weight_category: int
    ) -> float:
        """Load fraction for container type. Currently, containers are only distinguished according to their lengths.
        All fractions do not necessarily sum up to 1."""

        entry = ContainerWeightDistribution.get_or_none(
            (ContainerWeightDistribution.container_length == container_length)
            & (ContainerWeightDistribution.weight_category == container_weight_category)
        )
        if entry is None:
            raise MissingContainerWeightDistributionEntryException(
                f"container_length: {container_length}, container_weight_category: {container_weight_category}"
            )
        return entry.fraction

    @classmethod
    def get_distribution(cls) -> Dict[ContainerLength, Dict[int, float]]:
        """Loads a distribution for which all fractions are normalized to sum up to 1 for each container type.
        """
        container_weight_categories = [
            category_entry.weight_category
            for category_entry in list(ContainerWeightDistribution.select(
                ContainerWeightDistribution.weight_category
            ).distinct())]

        fractions = {
            container_length: {
                container_weight_category: cls._get_fraction_for_container_type(
                    container_length, container_weight_category)
                for container_weight_category in container_weight_categories
            }
            for container_length in ContainerLength
        }
        distributions = {}
        for container_length in ContainerLength:
            sum_over_container_length = sum(fractions[container_length].values())
            if sum_over_container_length > 0:  # This is the normal case
                distributions[container_length] = {
                    container_weight_category: (
                            fractions[container_length][container_weight_category] / sum_over_container_length
                    )
                    for container_weight_category in container_weight_categories
                }
            else:  # If all values are zeros, use uniform distribution.
                distributions[container_length] = {
                    container_weight_category: 1 / len(fractions[container_length])
                    for container_weight_category in container_weight_categories
                }
        return distributions
