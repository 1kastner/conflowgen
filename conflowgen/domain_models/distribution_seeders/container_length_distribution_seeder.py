from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength


def seed():
    """
    Seeds the database with some initial values for the length categories.

    The fraction of 60% forty-foot containers has been taken from expert interviews in the port of Hamburg.
    """
    ContainerLengthDistributionRepository.set_distribution({
        ContainerLength.twenty_feet: 0.4,
        ContainerLength.forty_feet: 0.6,
        ContainerLength.forty_five_feet: 0,
        ContainerLength.other: 0
    })
