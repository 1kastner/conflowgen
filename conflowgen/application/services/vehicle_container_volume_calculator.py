from __future__ import annotations

import datetime
import logging
import typing

from conflowgen.descriptive_datatypes import FlowDirection
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, AbstractLargeScheduledVehicle


class VehicleContainerVolumeCalculator:

    downscale_factor_during_ramp_up_period_for_outbound_transshipment = 0.2

    downscale_factor_during_ramp_down_period_for_inbound_all_kinds = 0.2

    def __init__(self):
        self.transportation_buffer = None
        self.ramp_up_period_end = None
        self.ramp_down_period_start = None
        self.logger = logging.getLogger("conflowgen")

    def set_transportation_buffer(
            self,
            transportation_buffer: float
    ) -> None:
        assert -1 < transportation_buffer
        self.transportation_buffer = transportation_buffer

    def set_ramp_up_and_down_times(
            self,
            ramp_up_period_end: typing.Optional[datetime.datetime] = None,
            ramp_down_period_start: typing.Optional[datetime.datetime] = None
    ) -> None:
        self.ramp_up_period_end = ramp_up_period_end
        self.ramp_down_period_start = ramp_down_period_start

    def get_transported_container_volume_on_inbound_journey(
            self,
            large_scheduled_vehicle: LargeScheduledVehicle | typing.Type[AbstractLargeScheduledVehicle],
    ) -> float:
        """

        Args:
            large_scheduled_vehicle: The vehicle for which the transported container volume is calculated for

        Returns:
            The container volume in TEU that are transported by this vehicle on its inbound journey. The volume is
            scaled down during the ramp-down period if present.
        """

        # auto-cast vehicles to their LargeScheduledVehicle reference
        if hasattr(large_scheduled_vehicle, "large_scheduled_vehicle"):
            large_scheduled_vehicle = large_scheduled_vehicle.large_scheduled_vehicle

        # This is our default
        moved_container_volume = large_scheduled_vehicle.inbound_container_volume

        if self.ramp_down_period_start is not None:
            arrival_time: datetime.datetime = large_scheduled_vehicle.scheduled_arrival
            if arrival_time >= self.ramp_down_period_start:
                moved_container_volume *= self.downscale_factor_during_ramp_down_period_for_inbound_all_kinds

        return moved_container_volume

    def get_maximum_transported_container_volume_on_outbound_journey(
            self,
            large_scheduled_vehicle: LargeScheduledVehicle | typing.Type[AbstractLargeScheduledVehicle],
            flow_direction: FlowDirection,
    ) -> (float, float):
        """

        Args:
            large_scheduled_vehicle: The vehicle for which the expected transported container volume is calculated for
            flow_direction: The flow direction to consider.

        Returns:
            The container volume in TEU that are transported by this vehicle on its outbound journey. The volume is
            scaled down during the ramp-down period if present for transshipment containers.
        """

        assert self.transportation_buffer is not None, "Transportation buffer must be set"
        assert -1 < self.transportation_buffer, "Transportation buffer must be larger than -1"

        # auto-cast vehicles to their LargeScheduledVehicle reference
        if hasattr(large_scheduled_vehicle, "large_scheduled_vehicle"):
            large_scheduled_vehicle = large_scheduled_vehicle.large_scheduled_vehicle

        # this is our default
        unscaled_moved_container_volume = self._get_maximum_outbound_capacity_in_teu(large_scheduled_vehicle)
        scaled_moved_container_volume = unscaled_moved_container_volume

        if self.ramp_up_period_end is not None and flow_direction == FlowDirection.transshipment_flow:
            arrival_time: datetime.datetime = large_scheduled_vehicle.scheduled_arrival
            if arrival_time <= self.ramp_up_period_end:
                scaled_moved_container_volume = (
                    unscaled_moved_container_volume
                    * self.downscale_factor_during_ramp_up_period_for_outbound_transshipment
                )

        return scaled_moved_container_volume, unscaled_moved_container_volume

    def _get_maximum_outbound_capacity_in_teu(
            self,
            large_scheduled_vehicle: LargeScheduledVehicle
    ) -> int:
        assert self.transportation_buffer is not None, "Please first set the transportation buffer!"
        expected_outbound_capacity_including_transportation_buffer = \
            large_scheduled_vehicle.inbound_container_volume * (1 + self.transportation_buffer)
        maximum_capacity_of_vehicle = large_scheduled_vehicle.capacity_in_teu
        maximum_outbound_capacity_in_teu = min(
            expected_outbound_capacity_including_transportation_buffer,
            maximum_capacity_of_vehicle
        )
        return maximum_outbound_capacity_in_teu
