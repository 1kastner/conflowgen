from __future__ import annotations

import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.descriptive_datatypes import VehicleIdentifier
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import LargeScheduledVehicle
from conflowgen.analyses.abstract_analysis import AbstractAnalysis


class InboundAndOutboundCapacity(typing.NamedTuple):
    """
    A vehicle identifier is a composition of the vehicle type, its service name, and the actual vehicle name
    """

    #: The capacity of the vehicle on its inbound journey in TEU
    inbound_capacity: float

    #: The capacity of the vehicle on its outbound journey in TEU
    outbound_capacity: float


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

    @DataSummariesCache.cache_result
    def get_inbound_and_outbound_capacity_of_each_vehicle(
            self,
            vehicle_type: typing.Any = "scheduled vehicles",
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> typing.Dict[VehicleIdentifier, typing.Tuple[float, float]]:
        """
        Args:
            vehicle_type: Either ``"scheduled vehicles"``, a single vehicle of type :class:`.ModeOfTransport` or a whole
                collection of vehicle types, e.g., passed as a :class:`list` or :class:`set`.
                Only the vehicles that correspond to the provided vehicle type(s) are considered in the analysis.
            start_date:
                Only include containers that arrive after the given start time.
            end_date:
                Only include containers that depart before the given end time.
        Returns:
            The transported containers of each vehicle on their inbound and outbound journey in TEU.
        """
        capacities: typing.Dict[VehicleIdentifier, InboundAndOutboundCapacity] = {}

        selected_vehicles = LargeScheduledVehicle.select().join(Schedule)
        if vehicle_type is not None and vehicle_type not in ("scheduled vehicles", "all"):
            selected_vehicles = self._restrict_vehicle_type(selected_vehicles, vehicle_type)

        vehicle: LargeScheduledVehicle
        for vehicle in selected_vehicles:

            # vehicle properties
            vehicle_name = vehicle.vehicle_name
            vehicle_arrival_time = vehicle.get_arrival_time()
            used_capacity_on_inbound_journey = vehicle.moved_capacity

            if start_date and vehicle_arrival_time < start_date:
                continue
            if end_date and vehicle_arrival_time > end_date:
                continue

            # schedule properties
            vehicle_schedule: Schedule = vehicle.schedule
            mode_of_transport = vehicle_schedule.vehicle_type
            service_name = vehicle_schedule.service_name

            used_capacity_on_outbound_journey = 0

            container: Container
            for container in Container.select().where(
                Container.picked_up_by_large_scheduled_vehicle == vehicle
            ):
                used_capacity_on_outbound_journey += container.occupied_teu

            vehicle_id = VehicleIdentifier(
                mode_of_transport=mode_of_transport,
                service_name=service_name,
                vehicle_name=vehicle_name,
                vehicle_arrival_time=vehicle_arrival_time
            )

            capacities[vehicle_id] = InboundAndOutboundCapacity(
                inbound_capacity=used_capacity_on_inbound_journey,
                outbound_capacity=used_capacity_on_outbound_journey
            )

        return capacities
