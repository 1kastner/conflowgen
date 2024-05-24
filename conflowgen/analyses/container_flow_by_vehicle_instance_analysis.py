from __future__ import annotations

import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.abstract_analysis import AbstractAnalysis
from conflowgen.descriptive_datatypes import VehicleIdentifier, FlowDirection


class ContainerFlowByVehicleInstanceAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerFlowByVehicleInstanceAnalysisReport`.
    """

    @staticmethod
    @DataSummariesCache.cache_result
    def get_container_flow_by_vehicle(
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> typing.Dict[
        ModeOfTransport, typing.Dict[VehicleIdentifier, typing.Dict[FlowDirection, (int, int)]]
    ]:
        """
        This shows for each of the vehicles

        Args:
            start_date:
                The earliest arriving container that is included. Consider all containers if :obj:`None`.
            end_date:
                The latest departing container that is included. Consider all containers if :obj:`None`.

        Returns:
            Grouped by vehicle type and vehicle instance, how much import, export, and transshipment is unloaded and
            loaded.
        """
        container_flow_by_vehicle: typing.Dict[
            ModeOfTransport, typing.Dict[VehicleIdentifier,
                                         typing.Dict[FlowDirection, typing.Dict[str, int]]]] = {
            vehicle_type: {}
            for vehicle_type in ModeOfTransport
        }

        vehicle_identifier_cache = {}

        container: Container
        for container in Container.select():
            if start_date and container.get_arrival_time() < start_date:
                continue
            if end_date and container.get_departure_time() > end_date:
                continue

            if container.delivered_by_large_scheduled_vehicle is not None:  # if not transported by truck

                if container.delivered_by_large_scheduled_vehicle not in vehicle_identifier_cache:
                    vehicle_id_inbound = VehicleIdentifier(
                        id=container.delivered_by_large_scheduled_vehicle.id,
                        mode_of_transport=container.delivered_by,
                        service_name=container.delivered_by_large_scheduled_vehicle.schedule.service_name,
                        vehicle_name=container.delivered_by_large_scheduled_vehicle.vehicle_name,
                        vehicle_arrival_time=container.get_arrival_time(),
                    )
                    vehicle_identifier_cache[container.delivered_by_large_scheduled_vehicle] = vehicle_id_inbound

                vehicle_id_inbound = vehicle_identifier_cache[container.delivered_by_large_scheduled_vehicle]

                if vehicle_id_inbound not in container_flow_by_vehicle[container.delivered_by]:
                    container_flow_by_vehicle[container.delivered_by][vehicle_id_inbound] = {
                        flow_direction: {
                            "inbound": 0,
                            "outbound": 0,
                        }
                        for flow_direction in FlowDirection
                    }
                container_flow_by_vehicle[
                    container.delivered_by][vehicle_id_inbound][container.flow_direction]["inbound"] += 1

            if container.picked_up_by_large_scheduled_vehicle is not None:  # if not transported by truck

                if container.picked_up_by_large_scheduled_vehicle not in vehicle_identifier_cache:
                    vehicle_id_outbound = VehicleIdentifier(
                        id=container.picked_up_by_large_scheduled_vehicle.id,
                        mode_of_transport=container.picked_up_by,
                        service_name=container.picked_up_by_large_scheduled_vehicle.schedule.service_name,
                        vehicle_name=container.picked_up_by_large_scheduled_vehicle.vehicle_name,
                        vehicle_arrival_time=container.get_departure_time(),
                    )
                    vehicle_identifier_cache[container.picked_up_by_large_scheduled_vehicle] = vehicle_id_outbound

                vehicle_id_outbound = vehicle_identifier_cache[container.picked_up_by_large_scheduled_vehicle]

                if vehicle_id_outbound not in container_flow_by_vehicle[container.picked_up_by]:
                    container_flow_by_vehicle[container.picked_up_by][vehicle_id_outbound] = {
                        flow_direction: {
                            "inbound": 0,
                            "outbound": 0,
                        }
                        for flow_direction in FlowDirection
                    }
                container_flow_by_vehicle[
                    container.picked_up_by][vehicle_id_outbound][container.flow_direction]["outbound"] += 1

        return container_flow_by_vehicle
