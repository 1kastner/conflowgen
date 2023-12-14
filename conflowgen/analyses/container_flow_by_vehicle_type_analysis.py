from __future__ import annotations

import copy
import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.abstract_analysis import AbstractAnalysis
from conflowgen.descriptive_datatypes import ContainerVolumeFromOriginToDestination


class ContainerFlowByVehicleTypeAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowByVehicleTypeAnalysisReport`.
    """

    @staticmethod
    @DataSummariesCache.cache_result
    def get_inbound_to_outbound_flow(
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> ContainerVolumeFromOriginToDestination:
        """
        This is the overview of the generated inbound to outbound container flow by vehicle type.

        Args:
            start_date:
                The earliest arriving container that is included. Consider all containers if :obj:`None`.
            end_date:
                The latest departing container that is included. Consider all containers if :obj:`None`.
        """
        inbound_to_outbound_flow_in_containers: typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]] = {
            vehicle_type_inbound:
                {
                    vehicle_type_outbound: 0
                    for vehicle_type_outbound in ModeOfTransport
                }
            for vehicle_type_inbound in ModeOfTransport
        }
        inbound_to_outbound_flow_in_teu = copy.deepcopy(inbound_to_outbound_flow_in_containers)

        container: Container
        for container in Container.select():
            if start_date and container.get_arrival_time() < start_date:
                continue
            if end_date and container.get_departure_time() > end_date:
                continue
            inbound_vehicle_type = container.delivered_by
            outbound_vehicle_type = container.picked_up_by
            inbound_to_outbound_flow_in_containers[inbound_vehicle_type][outbound_vehicle_type] += 1
            inbound_to_outbound_flow_in_teu[inbound_vehicle_type][outbound_vehicle_type] += container.occupied_teu

        inbound_to_outbound_flow = ContainerVolumeFromOriginToDestination(
            containers=inbound_to_outbound_flow_in_containers,
            teu=inbound_to_outbound_flow_in_teu
        )

        return inbound_to_outbound_flow
