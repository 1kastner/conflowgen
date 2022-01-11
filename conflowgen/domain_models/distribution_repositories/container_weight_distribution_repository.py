import math
from typing import Dict

from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthMissing


class MissingContainerWeightDistributionEntryException(Exception):
    pass


class ContainerWeightProbabilitiesUnequalOne(Exception):
    pass


class ContainerWeightProportionOutOfRangeException(Exception):
    pass


class ContainerWeightDistributionRepository:

    @staticmethod
    def _verify_container_weights(container_weights: Dict[ContainerLength, Dict[int, float]]):
        for container_length in ContainerLength:
            if container_length not in container_weights.keys():
                raise ContainerLengthMissing(container_length)

            container_weight_distribution_for_container_length = container_weights[container_length]
            total_probability_for_container_length = sum(container_weight_distribution_for_container_length.values())
            if not math.isclose(total_probability_for_container_length, 1):
                raise ContainerWeightProbabilitiesUnequalOne(
                    f"Container length: {container_length}, "
                    f"sum of all probabilities: {total_probability_for_container_length}"
                )

            for key, proportion in container_weight_distribution_for_container_length.items():
                if not (0 <= proportion <= 1):
                    raise ContainerWeightProportionOutOfRangeException(
                        f"Container length: {container_length}, "
                        f"key: {key}, value: {proportion}"
                    )

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

    def set_distribution(self, distribution: Dict[ContainerLength, Dict[int, float]]) -> None:
        self._verify_container_weights(distribution)
        raise NotImplementedError("Now, the container weight distribution must be saved in the peewee database")
