from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength


#: In general, most containerized goods are transported in 20' and 40' sea containers.
#: In Germany in August 2021, only 1% of containerized goods (measured in weight) were transported in a container
#: different from these two standard sizes :cite:p:`destatis.seeschifffahrt.august.2021`.
#: The same statistics says that approximately 30% of the goods (measured in weight again) are transported in 20'
#: containers, and 40' containers make up 67%.
#: For ConFlowGen, however, not the fraction of the weight is needed but the fraction in numbers of containers.
#: In an expert interview it was said that the TEU factor in their case is approximately 1.6 and 45 foot containers made
#: up less than 5%.
#:
#: The numbers used here are inspired by the statistics and the expert interview.
#: They are believed to be a reasonable first assumption if no other data is available.
DEFAULT_CONTAINER_LENGTH_FREQUENCIES = {
    ContainerLength.twenty_feet: 0.4,
    ContainerLength.forty_feet: 0.57,
    ContainerLength.forty_five_feet: 0.029,
    ContainerLength.other: 0.001
}


def seed():
    ContainerLengthDistributionRepository().set_distribution(
        DEFAULT_CONTAINER_LENGTH_FREQUENCIES
    )
