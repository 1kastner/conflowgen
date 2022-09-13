from __future__ import annotations

import datetime
from typing import Dict, Optional
import numpy as np

from conflowgen.domain_models.container import Container
from conflowgen.descriptive_datatypes import OutboundUsedAndMaximumCapacity, ContainerVolumeByVehicleType
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import LargeScheduledVehicle
from conflowgen.analyses.abstract_analysis import AbstractAnalysis


class InboundAndOutboundVehicleCapacityAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.InboundAndOutboundVehicleCapacityAnalysisReport`.
    """

    def __init__(self, transportation_buffer: float):
        super().__init__(
            transportation_buffer=transportation_buffer
        )

    @staticmethod
    def get_inbound_container_volumes_by_vehicle_type() -> ContainerVolumeByVehicleType:
        """
        This is the used capacity of all vehicles separated by vehicle type on their inbound journey in teu.
        """
        inbound_container_volume_in_teu: Dict[ModeOfTransport, float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }
        inbound_container_volume_in_containers = inbound_container_volume_in_teu.copy()

        container: Container
        for container in Container.select():
            inbound_vehicle_type = container.delivered_by
            teu_factor_of_container: float = ContainerLength.get_factor(container.length)
            inbound_container_volume_in_teu[inbound_vehicle_type] += teu_factor_of_container
            inbound_container_volume_in_containers[inbound_vehicle_type] += 1

        return ContainerVolumeByVehicleType(
            containers=inbound_container_volume_in_containers,
            teu=inbound_container_volume_in_teu
        )

    def get_outbound_container_volume_by_vehicle_type(
            self,
            start_time: Optional[datetime.datetime] = None,
            end_time: Optional[datetime.datetime] = None
    ) -> OutboundUsedAndMaximumCapacity:
        """
        This is the used and the maximum capacity of all vehicles separated by vehicle type on their outbound journey
        in TEU.
        If for a vehicle type, the used capacity is very close to the maximum capacity, you might want to
        reconsider the mode of transport distribution.
        See :class:`.ModeOfTransportDistributionManager` for further details.
        """
        assert self.transportation_buffer is not None

        outbound_actually_moved_container_volume_in_teu: Dict[ModeOfTransport, float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }
        outbound_actually_moved_container_volume_in_containers = outbound_actually_moved_container_volume_in_teu.copy()

        outbound_maximum_capacity_in_teu: Dict[ModeOfTransport, float] = {
            vehicle_type: 0
            for vehicle_type in ModeOfTransport
        }

        container: Container
        for container in Container.select():
            if start_time and container.get_arrival_time() < start_time:
                continue
            if end_time and container.get_departure_time() > end_time:
                continue
            outbound_vehicle_type: ModeOfTransport = container.picked_up_by
            teu_factor_of_container: float = ContainerLength.get_factor(container.length)
            outbound_actually_moved_container_volume_in_teu[outbound_vehicle_type] += teu_factor_of_container
            outbound_actually_moved_container_volume_in_containers[outbound_vehicle_type] += 1

        large_scheduled_vehicle: LargeScheduledVehicle
        for large_scheduled_vehicle in LargeScheduledVehicle.select():
            maximum_capacity_of_vehicle = min(
                int(large_scheduled_vehicle.moved_capacity * (1 + self.transportation_buffer)),
                large_scheduled_vehicle.capacity_in_teu
            )
            vehicle_type: ModeOfTransport = large_scheduled_vehicle.schedule.vehicle_type
            outbound_maximum_capacity_in_teu[vehicle_type] += maximum_capacity_of_vehicle

        outbound_maximum_capacity_in_teu[ModeOfTransport.truck] = np.nan  # Trucks can always be added as required

        return OutboundUsedAndMaximumCapacity(
            used=ContainerVolumeByVehicleType(
                containers=outbound_actually_moved_container_volume_in_containers,
                teu=outbound_actually_moved_container_volume_in_teu
            ),
            maximum=ContainerVolumeByVehicleType(
                containers=None,
                teu=outbound_maximum_capacity_in_teu
            )
        )
