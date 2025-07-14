from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength


#: In general, most containerized goods are transported in 20' and 40' sea containers.
#: In Germany in April 2025, less than 1% of containerized goods (measured in weight) were transported in a container
#: different from these two standard sizes :cite:p:`destatis2025seeschifffahrt`.
#: The same statistics says that ca. 30% of the goods (measured in weight again) are transported in 20'
#: containers, and ca. 70% in 40' containers.
#: For ConFlowGen, however, the fraction in numbers of containers is required instead of the fraction based on weight.
#: In an expert interview it was said that the TEU factor in their case is approximately 1.6 and 45 foot containers made
#: up less than 5%.
#:
#: The numbers used here are inspired by the reported statistics and the expert interview.
#: They are believed to be a reasonable first assumption if no data is available.
DEFAULT_CONTAINER_LENGTH_FREQUENCIES = {
    ContainerLength.twenty_feet: 0.4,
    ContainerLength.forty_feet: 0.57,
    ContainerLength.forty_five_feet: 0.029,
    ContainerLength.other: 0.001
}


def seed() -> None:
    ContainerLengthDistributionRepository().set_distribution(
        DEFAULT_CONTAINER_LENGTH_FREQUENCIES
    )
