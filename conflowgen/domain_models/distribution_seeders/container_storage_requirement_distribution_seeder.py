from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.distribution_repositories.container_storage_requirement_distribution_repository import \
    ContainerStorageRequirementDistributionRepository


DEFAULT_STORAGE_REQUIREMENT_FOR_ALL_LENGTHS = {
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

#: Containers come with different storage requirements.
#: The given distribution is estimated based on the combination of several sources.
#: Currently, no differentiation between the different container lengths exist.
DEFAULT_STORAGE_REQUIREMENT_DISTRIBUTION = {
    ContainerLength.twenty_feet: DEFAULT_STORAGE_REQUIREMENT_FOR_ALL_LENGTHS,
    ContainerLength.forty_feet: DEFAULT_STORAGE_REQUIREMENT_FOR_ALL_LENGTHS,
    ContainerLength.forty_five_feet: DEFAULT_STORAGE_REQUIREMENT_FOR_ALL_LENGTHS,
    ContainerLength.other: DEFAULT_STORAGE_REQUIREMENT_FOR_ALL_LENGTHS
}


def seed():
    ContainerStorageRequirementDistributionRepository().set_distribution(DEFAULT_STORAGE_REQUIREMENT_DISTRIBUTION)
