from __future__ import annotations

from typing import Dict, Tuple

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import LargeScheduledVehicle
from conflowgen.posthoc_analysis.abstract_posthoc_analysis import AbstractPosthocAnalysis


class InboundAndOutboundVehicleCapacityAnalysis(AbstractPosthocAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.InboundAndOutboundVehicleCapacityAnalysisReport`.
    """

    def __init__(self, transportation_buffer: float):
        super().__init__(
            transportation_buffer=transportation_buffer
        )

    def get_inbound_capacity_of_vehicles(self) -> Dict[ModeOfTransport, int]:
        """
        This is the used capacity of all vehicles separated by vehicle type on their inbound journey in TEU.

        .. todo:: Add capacity in containers for reporting the efficiency of the quay side (moves per hour)
        """
        inbound_capacity: Dict[ModeOfTransport, int | float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }

        container: Container
        for container in Container.select():
            inbound_vehicle_type = container.delivered_by
            teu_factor_of_container: float = ContainerLength.get_factor(container.length)
            inbound_capacity[inbound_vehicle_type] += teu_factor_of_container

        return inbound_capacity

    def get_outbound_capacity_of_vehicles(self) -> Tuple[Dict[ModeOfTransport, int], Dict[ModeOfTransport, int]]:
        """
        This is the used and the maximum capacity of all vehicles separated by vehicle type on their outbound journey
        in TEU. If for a vehicle type, the used capacity is very close to the maximum capacity, you might want to
        reconsider the mode of transport distribution. See :class:`.ModeOfTransportDistributionManager` for further
        details.

        .. todo:: Add capacity in containers for reporting the efficiency of the quay side (moves per hour)
        """
        outbound_actual_capacity: Dict[ModeOfTransport, int | float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }
        outbound_maximum_capacity: Dict[ModeOfTransport, int | float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }

        container: Container
        for container in Container.select():
            outbound_vehicle_type: ModeOfTransport = container.picked_up_by
            teu_factor_of_container: float = ContainerLength.get_factor(container.length)
            outbound_actual_capacity[outbound_vehicle_type] += teu_factor_of_container

        large_scheduled_vehicle: LargeScheduledVehicle
        for large_scheduled_vehicle in LargeScheduledVehicle.select():
            maximum_capacity_of_vehicle = min(
                large_scheduled_vehicle.moved_capacity * (1 + self.transportation_buffer),
                large_scheduled_vehicle.capacity_in_teu
            )
            vehicle_type: ModeOfTransport = large_scheduled_vehicle.schedule.vehicle_type
            outbound_maximum_capacity[vehicle_type] += maximum_capacity_of_vehicle

        outbound_maximum_capacity[ModeOfTransport.truck] = -1  # Not meaningful, trucks can always be added as required

        return outbound_actual_capacity, outbound_maximum_capacity
