from __future__ import annotations

import datetime
import typing

from peewee import ModelSelect

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

    @DataSummariesCache.cache_result
    def get_container_flow_by_vehicle(
            self,
            vehicle_types: typing.Collection[ModeOfTransport] = (
                ModeOfTransport.train,
                ModeOfTransport.feeder,
                ModeOfTransport.deep_sea_vessel,
                ModeOfTransport.barge
            ),
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None,
    ) -> [
        ModeOfTransport, typing.Dict[VehicleIdentifier, typing.Dict[FlowDirection, (int, int)]]
    ]:
        """
        Args:
            vehicle_types: A collection of vehicle types, e.g., passed as a :class:`list` or :class:`set`.
                Only the vehicles that correspond to the provided vehicle type(s) are considered in the analysis.
            start_date:
                The earliest arriving container that is included. Consider all containers if :obj:`None`.
            end_date:
                The latest departing container that is included. Consider all containers if :obj:`None`.

        Returns:
            Grouped by vehicle type and vehicle instance, how many import, export, and transshipment containers are
            unloaded and loaded (measured in TEU).
        """

        container_flow_by_vehicle: typing.Dict[
            ModeOfTransport, typing.Dict[VehicleIdentifier,
                                         typing.Dict[FlowDirection, typing.Dict[str, int]]]] = {
            vehicle_type: {}
            for vehicle_type in ModeOfTransport
        }

        vehicle_identifier_cache = {}

        selected_containers: ModelSelect = Container.select().where(
            (Container.delivered_by.in_(vehicle_types) | Container.picked_up_by.in_(vehicle_types))
        )

        container: Container
        for container in selected_containers:
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
                    container.delivered_by
                ][vehicle_id_inbound][container.flow_direction]["inbound"] += container.occupied_teu

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

        for skipped_vehicle_type in set(ModeOfTransport) - set(vehicle_types):
            assert len(container_flow_by_vehicle[skipped_vehicle_type]) == 0
            del container_flow_by_vehicle[skipped_vehicle_type]

        return container_flow_by_vehicle
