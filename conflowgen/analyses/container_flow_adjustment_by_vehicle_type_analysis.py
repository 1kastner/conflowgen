from __future__ import annotations

import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.abstract_analysis import AbstractAnalysis
from conflowgen.descriptive_datatypes import ContainerVolumeFromOriginToDestination


class ContainerFlowAdjustmentByVehicleTypeAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowAdjustmentByVehicleTypeAnalysisReport`.
    """

    @staticmethod
    @DataSummariesCache.cache_result
    def get_initial_to_adjusted_outbound_flow(
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> ContainerVolumeFromOriginToDestination:
        """
        When containers are generated, in order to obey the maximum dwell time, the vehicle type that is used for
        onward transportation might change. The initial outbound vehicle type is the vehicle type that is drawn
        randomly for a container at the time of generation. The adjusted vehicle type is the vehicle type that is drawn
        in case no vehicle of the initial outbound vehicle type is left within the maximum dwell time.

        Args:
            start_date:
                Only include containers that arrive after the given start time.
            end_date:
                Only include containers that depart before the given end time.

        Returns:
            The data structure describes how often an initial outbound vehicle type had to be adjusted with which other
            vehicle type.
        """

        # Initialize empty data structures
        initial_to_adjusted_outbound_flow_in_containers: typing.Dict[
            ModeOfTransport, typing.Dict[ModeOfTransport, float]] = {
            vehicle_type_initial:
                {
                    vehicle_type_adjusted: 0
                    for vehicle_type_adjusted in ModeOfTransport
                }
            for vehicle_type_initial in ModeOfTransport
        }
        initial_to_adjusted_outbound_flow_in_teu: typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]] = {
            vehicle_type_initial:
                {
                    vehicle_type_adjusted: 0
                    for vehicle_type_adjusted in ModeOfTransport
                }
            for vehicle_type_initial in ModeOfTransport
        }

        # Iterate over all containers and count number of containers / used teu capacity
        container: Container
        for container in Container.select():
            if start_date and container.get_arrival_time() < start_date:
                continue
            if end_date and container.get_departure_time() > end_date:
                continue
            vehicle_type_initial = container.picked_up_by_initial
            vehicle_type_adjusted = container.picked_up_by
            initial_to_adjusted_outbound_flow_in_containers[vehicle_type_initial][vehicle_type_adjusted] += 1
            initial_to_adjusted_outbound_flow_in_teu[vehicle_type_initial][vehicle_type_adjusted] += \
                container.occupied_teu

        return ContainerVolumeFromOriginToDestination(
            containers=initial_to_adjusted_outbound_flow_in_containers,
            teu=initial_to_adjusted_outbound_flow_in_teu
        )
