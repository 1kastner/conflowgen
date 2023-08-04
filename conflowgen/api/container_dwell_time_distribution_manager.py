import typing

from conflowgen.api.container_length_distribution_manager import ContainerLengthDistributionManager
from conflowgen.api.storage_requirement_distribution_manager import StorageRequirementDistributionManager
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.api import AbstractDistributionManager
from conflowgen.api.mode_of_transport_distribution_manager import ModeOfTransportDistributionManager
from conflowgen.application.services.inbound_and_outbound_vehicle_capacity import InboundAndOutboundVehicleCapacity
from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from conflowgen.tools.continuous_distribution import ContinuousDistribution


class ContainerDwellTimeDistributionManager(AbstractDistributionManager):
    """
    This is the interface to set and get the distribution that controls how long the container remains in the yard
    before it is loaded onto a vehicle and leaves again.
    """

    def __init__(self):
        self.container_dwell_time_distribution_repository = ContainerDwellTimeDistributionRepository()

    def get_container_dwell_time_distribution(
            self
    ) -> typing.Dict[ModeOfTransport, typing.Dict[
            ModeOfTransport, typing.Dict[StorageRequirement, ContinuousDistribution]]]:
        """

        Returns:
            The container dwell time distribution depends on the vehicle the container is delivered by, picked up by,
            and the storage requirement.
        """
        return self.container_dwell_time_distribution_repository.get_distributions()

    def set_container_dwell_time_distribution(
            self,
            distribution: typing.Dict[ModeOfTransport, typing.Dict[
                ModeOfTransport, typing.Dict[StorageRequirement, typing.Dict[str, typing.Any]]]]
    ) -> None:
        """
        The container dwell time distribution depends on the vehicle the container is delivered by, picked up by,
        and the storage requirement.

        A distribution is described by the following parameters:
            * distribution_name (:obj:`str`) - The name of the distribution.
            * average (:obj:`float`) - The expected mean
            * minimum (:obj:`float`) - The lower bound
            * maximum (:obj:`float`) - The upper bound

        Currently, the distributions 'lognormal' and 'uniform' are supported.
        """
        sanitized_distribution = self._normalize_and_validate_distribution_with_two_dependent_variables(
            distribution,
            ModeOfTransport,
            ModeOfTransport,
            StorageRequirement,
            values_are_frequencies=False
        )
        self.container_dwell_time_distribution_repository.set_distributions(
            sanitized_distribution
        )
        DataSummariesCache.reset_cache()

    def get_average_container_dwell_time(self, start_date, end_date) -> float:
        """
        Uses the inbound and outbound vehicle capacities service and the mode of transport input distribution
        to calculate the weighted average container dwell time.
        Returns:
            Weighted average of all container dwell times based on inbound and outbound vehicle capacities
        """
        inbound_vehicle_capacity = InboundAndOutboundVehicleCapacity.get_inbound_capacity_of_vehicles(
            start_date=start_date,
            end_date=end_date
        )
        mode_of_transport_distribution = ModeOfTransportDistributionManager().get_mode_of_transport_distribution()
        container_length_distribution = ContainerLengthDistributionManager().get_container_length_distribution()
        container_storage_requirement_distribution = \
            StorageRequirementDistributionManager().get_storage_requirement_distribution()
        container_dwell_time_distribution = self.get_container_dwell_time_distribution()
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
