from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.data_types.container_length import ContainerLength

DEFAULT_FORTY_AND_FORTY_FIVE_FEET_CONTAINER_WEIGHT_DISTRIBUTION = {
    2: 0,
    4: 2,
    6: 5,
    8: 6,
    10: 9,
    12: 11,
    14: 11,
    16: 9,
    18: 4,
    20: 3,
    22: 3,
    24: 3,
    26: 1,
    28: 1,
    30: 1
}

#: The initially seeded weight distributions stem from the cargo profile of the brochure
#: :cite:p:`macgregor2016containersecuring`.
#: The key refers to the weight of the container in metric tonnes.
#: The value describes the relative frequency.
DEFAULT_CONTAINER_WEIGHT_DISTRIBUTION = {
    ContainerLength.twenty_feet: {
        2: 1,
        4: 1,
        6: 2,
        8: 2.5,
        10: 2.5,
        12: 3,
        14: 3,
        16: 3,
        18: 2.5,
        20: 2.5,
        22: 2,
        24: 2,
        26: 2,
        28: 1,
        30: 1
    },
    ContainerLength.forty_feet: DEFAULT_FORTY_AND_FORTY_FIVE_FEET_CONTAINER_WEIGHT_DISTRIBUTION,
    ContainerLength.forty_five_feet: DEFAULT_FORTY_AND_FORTY_FIVE_FEET_CONTAINER_WEIGHT_DISTRIBUTION,
    ContainerLength.other: {
        weight_class: 0
        for weight_class in range(2, 32, 2)
    }
}


def seed():
    for container_length, distribution in DEFAULT_CONTAINER_WEIGHT_DISTRIBUTION.items():
        for container_weight_category, fraction in distribution.items():
            ContainerWeightDistribution.create(
                container_length=container_length,
                weight_category=container_weight_category,
                fraction=fraction
            )
