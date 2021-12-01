from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.data_types.container_length import ContainerLength


def _add_weight_distribution_category(
        container_length: ContainerLength,
        weight_category: int,
        fraction: float
) -> None:
    """Adds entry to the table. As there is no user interface, there is no repository interface.
    Thus the entries are created directly."""

    ContainerWeightDistribution.create(
        container_length=container_length,
        weight_category=weight_category,
        fraction=fraction
    )


def seed():
    """
    Seeds the database with some initial values for the weight categories.

    The initially seeded values stem from the cargo profile the brochure
    "Container securing systems - product catalogue" of MacGregor (Edition 101601, February 2016)
    URL: https://www.macgregor.com/globalassets/picturepark/imported-assets/65120.pdf
    """

    # 20 foot container
    _add_weight_distribution_category(ContainerLength.twenty_feet,  2,  1)
    _add_weight_distribution_category(ContainerLength.twenty_feet,  4,  1)
    _add_weight_distribution_category(ContainerLength.twenty_feet,  6,  2)
    _add_weight_distribution_category(ContainerLength.twenty_feet,  8,  2.5)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 10,  2.5)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 12,  3)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 14,  3)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 16,  3)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 18,  2.5)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 20,  2.5)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 22,  2)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 24,  2)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 26,  2)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 28,  1)
    _add_weight_distribution_category(ContainerLength.twenty_feet, 30,  1)

    # 40 foot container
    _add_weight_distribution_category(ContainerLength.forty_feet,  2,  0)
    _add_weight_distribution_category(ContainerLength.forty_feet,  4,  2)
    _add_weight_distribution_category(ContainerLength.forty_feet,  6,  5)
    _add_weight_distribution_category(ContainerLength.forty_feet,  8,  6)
    _add_weight_distribution_category(ContainerLength.forty_feet, 10,  9)
    _add_weight_distribution_category(ContainerLength.forty_feet, 12,  11)
    _add_weight_distribution_category(ContainerLength.forty_feet, 14,  11)
    _add_weight_distribution_category(ContainerLength.forty_feet, 16,  9)
    _add_weight_distribution_category(ContainerLength.forty_feet, 18,  4)
    _add_weight_distribution_category(ContainerLength.forty_feet, 20,  3)
    _add_weight_distribution_category(ContainerLength.forty_feet, 22,  3)
    _add_weight_distribution_category(ContainerLength.forty_feet, 24,  3)
    _add_weight_distribution_category(ContainerLength.forty_feet, 26,  1)
    _add_weight_distribution_category(ContainerLength.forty_feet, 28,  1)
    _add_weight_distribution_category(ContainerLength.forty_feet, 30,  1)

    # 45 foot container, same weight distribution as for 40 foot containers is assumed
    _add_weight_distribution_category(ContainerLength.forty_five_feet,  2,  0)
    _add_weight_distribution_category(ContainerLength.forty_five_feet,  4,  2)
    _add_weight_distribution_category(ContainerLength.forty_five_feet,  6,  5)
    _add_weight_distribution_category(ContainerLength.forty_five_feet,  8,  6)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 10,  9)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 12,  11)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 14,  11)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 16,  9)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 18,  4)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 20,  3)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 22,  3)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 24,  3)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 26,  1)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 28,  1)
    _add_weight_distribution_category(ContainerLength.forty_five_feet, 30,  1)

    for container_weight_category in range(2, 32, 2):
        _add_weight_distribution_category(ContainerLength.other, container_weight_category, 0)
