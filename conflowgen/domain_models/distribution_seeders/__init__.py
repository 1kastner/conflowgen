from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder, \
    container_weight_distribution_seeder, container_length_distribution_seeder, truck_arrival_distribution_seeder, \
    container_storage_requirement_distribution_seeder, container_dwell_time_distribution_seeder


def seed_all_distributions(**options) -> None:
    """
    Seeds all databases with default values

    Args:
        **options: This allows to select different default values that are passed through to the seeder functions.
    """
    mode_of_transport_distribution_seeder.seed()
    container_dwell_time_distribution_seeder.seed()
    container_weight_distribution_seeder.seed()
    container_length_distribution_seeder.seed()
    if "assume_tas" in options:
        truck_arrival_distribution_seeder.seed(assume_tas=options["assume_tas"])
    else:
        truck_arrival_distribution_seeder.seed()
    container_storage_requirement_distribution_seeder.seed()
