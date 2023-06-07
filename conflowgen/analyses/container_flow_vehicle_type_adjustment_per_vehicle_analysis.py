from __future__ import annotations

import collections
import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.abstract_analysis import AbstractAnalysis
from conflowgen.descriptive_datatypes import VehicleIdentifier


class ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysisReport`.
    """
    @DataSummariesCache.cache_result
    def get_vehicle_type_adjustments_per_vehicle(
            self,
            initial_vehicle_type: ModeOfTransport | str | typing.Collection = "scheduled vehicles",
            adjusted_vehicle_type: ModeOfTransport | str | typing.Collection = "scheduled vehicles",
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> typing.Dict[VehicleIdentifier, int]:
        """
        When containers are generated, in order to obey the maximum dwell time, the vehicle type that is used for
        onward transportation might change. The initial outbound vehicle type is the vehicle type that is drawn
        randomly for a container at the time of generation. The adjusted vehicle type is the vehicle type that is drawn
        in case no vehicle of the initial outbound vehicle type is left within the maximum dwell time.

        Args:
            initial_vehicle_type: Either ``"all"``, ``scheduled vehicles``, a single vehicle of type
                :class:`.ModeOfTransport` or a whole
                collection of vehicle types, e.g., passed as a :class:`list` or :class:`set`.
                Only the vehicles that correspond to the provided vehicle type(s) are considered in the analysis.
            adjusted_vehicle_type: Either ``"all"``, ``scheduled vehicles``, a single vehicle of type
                :class:`.ModeOfTransport` or a whole
                collection of vehicle types, e.g., passed as a :class:`list` or :class:`set`.
                Only the vehicles that correspond to the provided vehicle type(s) are considered in the analysis.
            start_date:
                Only include containers that arrive after the given start time.
            end_date:
                Only include containers that depart before the given end time.
        Returns:
            The data structure describes how often an initial outbound vehicle type had to be adjusted over time
            in relation to the total container flows.
        """

        # Initialize empty data structures
        number_of_non_adjusted_containers_per_vehicle: typing.Dict[VehicleIdentifier, int] = collections.Counter()
        number_of_adjusted_containers_per_vehicle: typing.Dict[VehicleIdentifier, int] = collections.Counter()

        selected_containers = Container.select()

        if initial_vehicle_type is not None and initial_vehicle_type != "all":
            selected_containers = self._restrict_container_picked_up_by_initial_vehicle_type(
                selected_containers, initial_vehicle_type
            )

        if adjusted_vehicle_type is not None and adjusted_vehicle_type != "all":
            selected_containers = self._restrict_container_picked_up_by_vehicle_type(
                selected_containers, adjusted_vehicle_type
            )

        vehicle_identifiers: typing.List[VehicleIdentifier] = []

        container: Container
        for container in selected_containers:
            if start_date and container.get_arrival_time() < start_date:
                continue
            if end_date and container.get_departure_time() > end_date:
                continue

            vehicle_identifier = self._get_vehicle_identifier_for_vehicle_picking_up_the_container(container)

            container_vehicle_type_has_been_adjusted = (container.picked_up_by != container.picked_up_by_initial)

            if container_vehicle_type_has_been_adjusted:
                number_of_adjusted_containers_per_vehicle[vehicle_identifier] += 1
            else:
                number_of_non_adjusted_containers_per_vehicle[vehicle_identifier] += 1

            vehicle_identifiers.append(vehicle_identifier)

        fraction_of_adjusted_containers = {
            vehicle_identifier: number_of_adjusted_containers_per_vehicle[vehicle_identifier] / (
                number_of_adjusted_containers_per_vehicle[vehicle_identifier]
                + number_of_non_adjusted_containers_per_vehicle[vehicle_identifier]
            )
            for vehicle_identifier in vehicle_identifiers
        }

        return fraction_of_adjusted_containers

    @staticmethod
    def _get_vehicle_identifier_for_vehicle_picking_up_the_container(container: Container) -> VehicleIdentifier:
        if container.picked_up_by == ModeOfTransport.truck:
            vehicle_identifier = VehicleIdentifier(
                mode_of_transport=ModeOfTransport.truck,
                vehicle_arrival_time=container.get_departure_time(),
                service_name=None,
                vehicle_name=None
            )
        else:
            vehicle_identifier = VehicleIdentifier(
                mode_of_transport=container.picked_up_by,
                vehicle_arrival_time=container.get_departure_time(),
                service_name=container.picked_up_by_large_scheduled_vehicle.schedule.service_name,
                vehicle_name=container.picked_up_by_large_scheduled_vehicle.vehicle_name
            )
        return vehicle_identifier
