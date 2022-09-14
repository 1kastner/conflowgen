from __future__ import annotations

import datetime
from typing import Dict, NamedTuple, Tuple, Any

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import LargeScheduledVehicle
from conflowgen.analyses.abstract_analysis import AbstractAnalysis


class CompleteVehicleIdentifier(NamedTuple):
    """
    A vehicle identifier is a composition of the vehicle type, its service name, and the actual vehicle name
    """
    mode_of_transport: ModeOfTransport
    service_name: str
    vehicle_name: str


class InboundToOutboundVehicleCapacityUtilizationAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.InboundToOutboundCapacityUtilizationAnalysisReport`.
    """

    def __init__(self, transportation_buffer: float):
        super().__init__(
            transportation_buffer=transportation_buffer
        )

    def get_inbound_and_outbound_capacity_of_each_vehicle(
            self,
            vehicle_type: Any = "all"
    ) -> Dict[CompleteVehicleIdentifier, Tuple[datetime.datetime, float, float]]:
        """
        Args:
            vehicle_type: Either ``"all"``, a single vehicle of type :class:`.ModeOfTransport` or a whole collection of
                vehicle types, e.g., passed as a :class:`list` or :class:`set`.
                Only the vehicles that correspond to the provided vehicle type(s) are considered in the analysis.

        Returns:
            The transported containers of each vehicle on their inbound and outbound journey in TEU.
        """
        capacities: Dict[CompleteVehicleIdentifier, (float, float)] = {}

        selected_vehicles = LargeScheduledVehicle.select().join(Schedule)
        if vehicle_type is not None and vehicle_type != "all":
            selected_vehicles = self._restrict_vehicle_type(selected_vehicles, vehicle_type)

        vehicle: LargeScheduledVehicle
        for vehicle in selected_vehicles:
            vehicle_schedule: Schedule = vehicle.schedule
            mode_of_transport = vehicle_schedule.vehicle_type
            service_name = vehicle_schedule.service_name
            vehicle_name = vehicle.vehicle_name
            used_capacity_on_inbound_journey = vehicle.moved_capacity

            used_capacity_on_outbound_journey = 0

            container: Container
            for container in Container.select().where(
                Container.picked_up_by_large_scheduled_vehicle == vehicle
            ):
                used_capacity_on_outbound_journey += container.occupied_teu

            vehicle_id = CompleteVehicleIdentifier(
                mode_of_transport=mode_of_transport,
                service_name=service_name,
                vehicle_name=vehicle_name
            )

            vehicle_arrival = datetime.datetime.combine(
                vehicle_schedule.vehicle_arrives_at, vehicle_schedule.vehicle_arrives_at_time
            )

            capacities[vehicle_id] = (
                vehicle_arrival, used_capacity_on_inbound_journey, used_capacity_on_outbound_journey
            )

        return capacities
