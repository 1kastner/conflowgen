import datetime

from conflowgen.api.container_length_distribution_manager import ContainerLengthDistributionManager
from conflowgen.api.mode_of_transport_distribution_manager import ModeOfTransportDistributionManager
from conflowgen.api.storage_requirement_distribution_manager import StorageRequirementDistributionManager
from conflowgen.application.services.inbound_and_outbound_vehicle_capacity_calculator_service import \
    InboundAndOutboundVehicleCapacityCalculatorService
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository


class AverageContainerDwellTimeCalculatorService:

    def get_average_container_dwell_time(self, start_date: datetime.date, end_date: datetime.date) -> float:
        inbound_vehicle_capacity = InboundAndOutboundVehicleCapacityCalculatorService.get_inbound_capacity_of_vehicles(
            start_date=start_date,
            end_date=end_date
        )
        mode_of_transport_distribution = ModeOfTransportDistributionManager().get_mode_of_transport_distribution()
        container_length_distribution = ContainerLengthDistributionManager().get_container_length_distribution()
        container_storage_requirement_distribution = \
            StorageRequirementDistributionManager().get_storage_requirement_distribution()
        container_dwell_time_distribution = ContainerDwellTimeDistributionRepository(). \
            get_distributions()
        average_container_dwell_time = 0
        total_containers = 0
        for delivering_vehicle_type in ModeOfTransport:
            for picking_up_vehicle_type in ModeOfTransport:
                for container_length in ContainerLength:
                    for storage_requirement in StorageRequirement:
                        num_containers = inbound_vehicle_capacity.containers[delivering_vehicle_type] * \
                                         mode_of_transport_distribution[delivering_vehicle_type][
                                             picking_up_vehicle_type] * \
                                         container_length_distribution[container_length] * \
                                         container_storage_requirement_distribution[container_length][
                                             storage_requirement]
                        total_containers += num_containers
                        average_container_dwell_time += \
                            container_dwell_time_distribution[delivering_vehicle_type][picking_up_vehicle_type][
                                storage_requirement].average * num_containers

        average_container_dwell_time /= total_containers
        return average_container_dwell_time
