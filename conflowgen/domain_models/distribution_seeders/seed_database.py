from conflowgen.domain_models.distribution_seeders import container_weight_distribution_seeder, \
    truck_arrival_distribution_seeder, mode_of_transport_distribution_seeder, container_length_distribution_seeder, \
    container_storage_requirement_distribution_seeder


def seed_all_distributions():
    """Seeds all databases with default values"""
    mode_of_transport_distribution_seeder.seed()
    container_weight_distribution_seeder.seed()
    container_length_distribution_seeder.seed()
    truck_arrival_distribution_seeder.seed()
    container_storage_requirement_distribution_seeder.seed()
