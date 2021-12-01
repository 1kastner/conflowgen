from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.distribution_repositories.container_storage_requirement_distribution_repository import \
    ContainerStorageRequirementDistributionRepository

default_values = {
    # Whatever is not an empty, a reefer or a dangerous goods container is considered a standard container.
    # Formula: All containers minus number of empties minus number of reefers and of that ninety percent
    StorageRequirement.standard: (1 - .12 - .07) * 0.9,

    # See https://www.hafen-hamburg.de/de/statistiken/containerumschlag/
    StorageRequirement.empty: .12,

    # See e.g. https://hhla.de/unternehmen/tochterunternehmen/container-terminal-altenwerder-cta/technische-daten
    # and compare the number of container slots in the yard for reefers with other types of containers.
    StorageRequirement.reefer: .07,

    # See https://www.ukpandi.com/news-and-resources/bulletins/2016/safe-carriage-of-dangerous-goods-in-containers/
    # Formula: All containers minus number of empties minus number of reefers and of that ten percent
    StorageRequirement.dangerous_goods: (1 - .12 - .07) * 0.1
}


def seed():
    """
    Seeds the database with some initial values. Currently, for all container lengths the same default values are used.
    The default values are reverse-engineered based on several news articles.
    """
    ContainerStorageRequirementDistributionRepository().set_distribution({
        ContainerLength.twenty_feet: default_values,
        ContainerLength.forty_feet: default_values,
        ContainerLength.forty_five_feet: default_values,
        ContainerLength.other: default_values
    })
