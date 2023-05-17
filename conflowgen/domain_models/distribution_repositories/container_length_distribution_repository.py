import math
from typing import Dict

from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.data_types.container_length import ContainerLength


class ContainerLengthDistributionTableWithDuplicatesException(Exception):
    pass


class ContainerLengthMissing(Exception):
    pass


class ContainerLengthProportionOutOfRangeException(Exception):
    pass


class ContainerLengthProportionsUnequalOneException(Exception):
    pass


class ContainerLengthDistributionRepository:

    @staticmethod
    def _verify_container_lengths(container_lengths: Dict[ContainerLength, float]):
        for container_length in ContainerLength:
            if container_length not in container_lengths.keys():
                raise ContainerLengthMissing(container_length)
            container_length_proportion = container_lengths[container_length]
            if not (0 <= container_length_proportion <= 1):
                raise ContainerLengthProportionOutOfRangeException(container_length_proportion)
        sum_of_all_proportions = sum(container_lengths.values())
        if not math.isclose(sum_of_all_proportions, 1):
            raise ContainerLengthProportionsUnequalOneException(sum_of_all_proportions)

    @classmethod
    def get_distribution(cls) -> Dict[ContainerLength, float]:
        container_length_distribution_entry: ContainerLengthDistribution
        return {
            container_length_distribution_entry.container_length:  # pylint: disable=undefined-variable
            container_length_distribution_entry.fraction  # pylint: disable=undefined-variable
            for container_length_distribution_entry in ContainerLengthDistribution.select()
        }

    @classmethod
    def set_distribution(cls, container_lengths: Dict[ContainerLength, float]):
        cls._verify_container_lengths(container_lengths)
        ContainerLengthDistribution.delete().execute()
        for container_length, fraction in container_lengths.items():
            ContainerLengthDistribution.create(
                container_length=container_length,
                fraction=fraction
            ).save()

    @classmethod
    def get_teu_factor(cls) -> float:
        """
        Calculates and returns the TEU factor based on the container length distribution.
        """
        # Loop through container lengths and calculate weighted average of all container lengths
        container_length_weighted_average = 0.0
        container_length_distribution = cls.get_distribution()
        for container_length, fraction in container_length_distribution.items():
            container_length_weighted_average += ContainerLength.get_factor(container_length) * fraction
        return container_length_weighted_average
