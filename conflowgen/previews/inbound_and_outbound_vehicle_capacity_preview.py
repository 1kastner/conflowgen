from __future__ import annotations
import datetime
from typing import Dict
import numpy as np

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.descriptive_datatypes import OutboundUsedAndMaximumCapacity, ContainerVolumeByVehicleType
from conflowgen.domain_models.distribution_validators import validate_distribution_with_one_dependent_variable
from conflowgen.previews.abstract_preview import AbstractPreview
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.factories.fleet_factory import create_arrivals_within_time_range
from conflowgen.domain_models.large_vehicle_schedule import Schedule


class InboundAndOutboundVehicleCapacityPreview(AbstractPreview):
    """
    This preview examines how much the inbound vehicles deliver to the terminal and how it is redistributed to the
    outbound journeys of the other vehicles according to the mode of transport distribution.
    This pre-checks whether the transport capacity of the vehicles will be exceeded.
    In such case, the input schedules and distributions should be further refined before generating a container flow.

    The preview returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.InboundAndOutboundVehicleCapacityPreviewReport`.
    The preview is intended to provide a first estimate before running the expensive
    :meth:`.ContainerFlowGenerationManager.generate` method.
    The preview does not consider all restrictions (such as container dwell times in combination with the schedules)
    into consideration, thus later deviations might exist.
    """

    def __init__(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            transportation_buffer: float
    ):
        """
        Args:
            start_date: The earliest day to consider when checking the vehicles that move according to schedules
            end_date: The latest day to consider when checking the vehicles that move according to schedules
            transportation_buffer: The fraction of how much more a vehicle takes with it on an outbound journey
                compared to an inbound journey as long as the total vehicle capacity is not exceeded.
        """
        super().__init__(
            start_date=start_date,
            end_date=end_date,
            transportation_buffer=transportation_buffer
        )

        self.mode_of_transport_distribution = ModeOfTransportDistributionRepository().get_distribution()

    @DataSummariesCache.cache_result
    def _get_truck_capacity_for_export_containers(
            self,
            inbound_capacity_of_vehicles: Dict[ModeOfTransport, float]
    ) -> float:
        """
        Get the capacity in TEU which is transported by truck. Currently, during the generation process each import
        container is picked up by one truck and for each import container, in the next step one export container is
        created.
        Thus, this method accounts for both import and export.
        """
        truck_capacity = 0
        for vehicle_type in ModeOfTransport.get_scheduled_vehicles():
            number_of_containers_delivered_to_terminal_by_vehicle_type = inbound_capacity_of_vehicles[vehicle_type]
            mode_of_transport_distribution_of_vehicle_type = self.mode_of_transport_distribution[vehicle_type]
            vehicle_to_truck_fraction = mode_of_transport_distribution_of_vehicle_type[ModeOfTransport.truck]
            number_of_containers_to_pick_up_by_truck_from_vehicle_type = \
                number_of_containers_delivered_to_terminal_by_vehicle_type * vehicle_to_truck_fraction
            truck_capacity += number_of_containers_to_pick_up_by_truck_from_vehicle_type
        return truck_capacity

    @DataSummariesCache.cache_result
    def hypothesize_with_mode_of_transport_distribution(
            self,
            mode_of_transport_distribution: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
    ):
        validate_distribution_with_one_dependent_variable(
            mode_of_transport_distribution, ModeOfTransport, ModeOfTransport, values_are_frequencies=True
        )
        self.mode_of_transport_distribution = mode_of_transport_distribution

    @DataSummariesCache.cache_result
    def get_inbound_capacity_of_vehicles(self) -> ContainerVolumeByVehicleType:
        """
        For the inbound capacity, first vehicles that adhere to a schedule are considered. Trucks, which are created
        depending on the outbound distribution, are created based on the assumptions of the further container flow
        generation process.
        """
        inbound_capacity_in_teu: Dict[ModeOfTransport, float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }

        for schedule in Schedule.select():
            arrivals = create_arrivals_within_time_range(
                self.start_date,
                schedule.vehicle_arrives_at,
                self.end_date,
                schedule.vehicle_arrives_every_k_days,
                schedule.vehicle_arrives_at_time
            )
            total_capacity_moved_by_vessel = (len(arrivals)  # number of vehicles that are planned
                                              * schedule.average_moved_capacity)  # TEU capacity of each vehicle
            inbound_capacity_in_teu[schedule.vehicle_type] += total_capacity_moved_by_vessel

        inbound_capacity_in_teu[ModeOfTransport.truck] = self._get_truck_capacity_for_export_containers(
            inbound_capacity_in_teu
        )

        return ContainerVolumeByVehicleType(
            containers=None,
            teu=inbound_capacity_in_teu
        )

    @DataSummariesCache.cache_result
    def get_outbound_capacity_of_vehicles(self) -> OutboundUsedAndMaximumCapacity:
        """
        For the outbound capacity, both the used outbound capacity (estimated) and the maximum outbound capacity is
        reported. If a vehicle type reaches the maximum outbound capacity, this means that containers need to be
        redistributed to other vehicle types due to a lack of capacity. The capacities are only calculated in TEU, not
        in containers.
        """
        outbound_used_capacity_in_teu: Dict[ModeOfTransport, float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }
        outbound_maximum_capacity_in_teu: Dict[ModeOfTransport, float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }

        schedule: Schedule
        for schedule in Schedule.select():

            assert schedule.average_moved_capacity <= schedule.average_vehicle_capacity, \
                "A vehicle cannot move a larger amount of containers (in TEU) than its capacity, " \
                f"the input data is malformed. Schedule '{schedule.service_name}' of vehicle type " \
                f"{schedule.vehicle_type} has an average moved capacity of {schedule.average_moved_capacity} but an " \
                f"averaged vehicle capacity of {schedule.average_vehicle_capacity}."

            arrivals = create_arrivals_within_time_range(
                self.start_date,
                schedule.vehicle_arrives_at,
                self.end_date,
                schedule.vehicle_arrives_every_k_days,
                schedule.vehicle_arrives_at_time
            )

            # If all container flows are balanced, only the average moved capacity is required
            total_average_capacity_moved_by_vessel_in_teu = len(arrivals) * schedule.average_moved_capacity
            outbound_used_capacity_in_teu[schedule.vehicle_type] += total_average_capacity_moved_by_vessel_in_teu

            # If there are unbalanced container flows, a vehicle departs with more containers than it delivered
            maximum_capacity_of_vehicle_in_teu = min(
                schedule.average_moved_capacity * (1 + self.transportation_buffer),
                schedule.average_vehicle_capacity
            )
            total_maximum_capacity_moved_by_vessel = len(arrivals) * maximum_capacity_of_vehicle_in_teu
            outbound_maximum_capacity_in_teu[schedule.vehicle_type] += total_maximum_capacity_moved_by_vessel

        inbound_capacity = self.get_inbound_capacity_of_vehicles()
        outbound_used_capacity_in_teu[ModeOfTransport.truck] = self._get_truck_capacity_for_export_containers(
            inbound_capacity.teu
        )
        outbound_maximum_capacity_in_teu[ModeOfTransport.truck] = np.nan  # Trucks can always be added as required

        return OutboundUsedAndMaximumCapacity(
            used=ContainerVolumeByVehicleType(
                containers=None,
                teu=outbound_used_capacity_in_teu
            ),
            maximum=ContainerVolumeByVehicleType(
                containers=None,
                teu=outbound_maximum_capacity_in_teu
            )
        )
