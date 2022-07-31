import logging

import peewee

from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForPickup, \
    TruckArrivalInformationForDelivery
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
from conflowgen.domain_models.vehicle import DeepSeaVessel, Feeder, LargeScheduledVehicle, Train, Barge, Truck

logger = logging.getLogger("conflowgen")


def create_tables(sql_db_connection: peewee.Database) -> peewee.Database:
    logger.debug("Creating all tables...")
    sql_db_connection.create_tables([
        Container,
        Destination,
        LargeScheduledVehicle,
        DeepSeaVessel,
        Train,
        Feeder,
        Barge,
        LargeScheduledVehicle,
        Truck,
        Schedule,
        ModeOfTransportDistribution,
        ContainerWeightDistribution,
        ContainerLengthDistribution,
        ContainerFlowGenerationProperties,
        TruckArrivalDistribution,
        TruckArrivalInformationForPickup,
        TruckArrivalInformationForDelivery,
        StorageRequirementDistribution,
        ContainerDwellTimeDistribution
    ])
    for table_with_index in (
        Destination,
    ):
        table_with_index.initialize_index()
    return sql_db_connection
