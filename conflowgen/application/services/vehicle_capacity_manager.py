import datetime
import logging
import typing
from typing import Dict, Callable, Type

from conflowgen.application.services.vehicle_container_volume_calculator import VehicleContainerVolumeCalculator
from conflowgen.descriptive_datatypes import FlowDirection
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, AbstractLargeScheduledVehicle


class VehicleCapacityManager:

    ignored_capacity = ContainerLength.get_teu_factor(ContainerLength.other)

    def __init__(self):
        self.vehicle_container_volume_calculator = VehicleContainerVolumeCalculator()
        self.occupied_capacity_for_outbound_journey_buffer: (
            Dict)[Type[AbstractLargeScheduledVehicle], float] = {}
        self.occupied_capacity_for_inbound_journey_buffer: (
            Dict)[Type[AbstractLargeScheduledVehicle], float] = {}
        self.logger = logging.getLogger("conflowgen")

    def set_transportation_buffer(self, transportation_buffer: float):
        self.vehicle_container_volume_calculator.set_transportation_buffer(transportation_buffer)

    def set_ramp_up_and_down_times(
            self,
            ramp_up_period_end: typing.Optional[datetime.datetime] = None,
            ramp_down_period_start: typing.Optional[datetime.datetime] = None,
    ) -> None:
        self.vehicle_container_volume_calculator.set_ramp_up_and_down_times(
            ramp_up_period_end=ramp_up_period_end,
            ramp_down_period_start=ramp_down_period_start,
        )

    def reset_cache(self):
        self.occupied_capacity_for_inbound_journey_buffer = {}
        self.occupied_capacity_for_outbound_journey_buffer = {}

    def block_capacity_for_inbound_journey(
            self,
            vehicle: Type[AbstractLargeScheduledVehicle],
            container: Container
    ) -> bool:
        assert vehicle in self.occupied_capacity_for_inbound_journey_buffer, \
            "First .get_free_capacity_for_inbound_journey(vehicle) must be invoked"

        usable_vessel_capacity = self.vehicle_container_volume_calculator.\
            get_transported_container_volume_on_inbound_journey(vehicle)

        occupied_capacity_in_teu = self.occupied_capacity_for_inbound_journey_buffer[vehicle]
        used_capacity_in_teu = ContainerLength.get_teu_factor(container_length=container.length)
        new_occupied_capacity_in_teu = occupied_capacity_in_teu + used_capacity_in_teu

        new_free_capacity_in_teu = usable_vessel_capacity - new_occupied_capacity_in_teu
        assert (
            new_free_capacity_in_teu >= 0,
            f"vehicle {vehicle} is overloaded, "
            f"usable_vessel_capacity: {usable_vessel_capacity}, "
            f"occupied_capacity_in_teu: {occupied_capacity_in_teu}, "
            f"used_capacity_in_teu: {used_capacity_in_teu}, "
            f"new_free_capacity_in_teu: {new_free_capacity_in_teu}"
        )

        self.occupied_capacity_for_inbound_journey_buffer[vehicle] = new_occupied_capacity_in_teu
        vehicle_capacity_is_exhausted = new_free_capacity_in_teu < self.ignored_capacity
        return vehicle_capacity_is_exhausted

    def block_capacity_for_outbound_journey(
            self,
            vehicle: Type[AbstractLargeScheduledVehicle],
            container: Container
    ) -> bool:
        assert vehicle in self.occupied_capacity_for_outbound_journey_buffer, \
            "First .get_free_capacity_for_outbound_journey(vehicle) must be invoked"

        scaled_moved_container_volume, unscaled_moved_container_volume = self.vehicle_container_volume_calculator.\
            get_maximum_transported_container_volume_on_outbound_journey(vehicle, container.flow_direction)

        # calculate new free capacity
        occupied_capacity_in_teu = self.occupied_capacity_for_outbound_journey_buffer[vehicle]
        used_capacity_in_teu = ContainerLength.get_teu_factor(container_length=container.length)
        new_occupied_capacity_in_teu = occupied_capacity_in_teu + used_capacity_in_teu

        new_scaled_free_capacity_in_teu = scaled_moved_container_volume - new_occupied_capacity_in_teu

        new_unscaled_free_capacity_in_teu = unscaled_moved_container_volume - new_occupied_capacity_in_teu
        assert (
            new_unscaled_free_capacity_in_teu >= 0,
            f"vehicle {vehicle} is overloaded, "
            f"scaled_moved_container_volume: {scaled_moved_container_volume}, "
            f"unscaled_moved_container_volume: {unscaled_moved_container_volume}, "
            f"occupied_capacity_in_teu: {occupied_capacity_in_teu}, "
            f"used_capacity_in_teu: {used_capacity_in_teu}, "
            f"new_scaled_free_capacity_in_teu: {new_scaled_free_capacity_in_teu} "
            f"new_unscaled_free_capacity_in_teu: {new_unscaled_free_capacity_in_teu}"
        )

        self.occupied_capacity_for_outbound_journey_buffer[vehicle] = new_occupied_capacity_in_teu

        space_is_exhausted = (new_scaled_free_capacity_in_teu <= self.ignored_capacity)
        return space_is_exhausted

    # noinspection PyTypeChecker
    def get_free_capacity_for_inbound_journey(self, vehicle: Type[AbstractLargeScheduledVehicle]) -> float:
        """
        Get the free capacity for the inbound journey on a vehicle that moves according to a schedule in TEU.
        During the ramp-down period (if existent), all inbound traffic is scaled down, no matter what.
        """
        inbound_container_volume = self.vehicle_container_volume_calculator\
            .get_transported_container_volume_on_inbound_journey(vehicle)

        if vehicle in self.occupied_capacity_for_inbound_journey_buffer:
            occupied_capacity_in_teu = self.occupied_capacity_for_inbound_journey_buffer[vehicle]
        else:
            occupied_capacity_in_teu = self._get_occupied_capacity_in_teu(
                vehicle=vehicle,
                container_counter=self._get_number_containers_for_inbound_journey,
            )
            self.occupied_capacity_for_inbound_journey_buffer[vehicle] = occupied_capacity_in_teu

        free_capacity_in_teu = inbound_container_volume - occupied_capacity_in_teu
        return free_capacity_in_teu

    def get_free_capacity_for_outbound_journey(
            self, vehicle: Type[AbstractLargeScheduledVehicle],
            flow_direction: FlowDirection
    ) -> float:
        """
        Get the free capacity for the outbound journey on a vehicle that moves according to a schedule in TEU.
        During the ramp-up period (if existent), all outbound traffic that constitutes transshipment, is scaled down.
        """

        # During the ramp-up period, the container volume is reduced at this stage
        maximum_transported_container_volume, unscaled_moved_container_volume = \
            self.vehicle_container_volume_calculator.get_maximum_transported_container_volume_on_outbound_journey(
                vehicle, flow_direction
            )

        if vehicle in self.occupied_capacity_for_outbound_journey_buffer:
            occupied_capacity_in_teu = self.occupied_capacity_for_outbound_journey_buffer[vehicle]
        else:
            occupied_capacity_in_teu = self._get_occupied_capacity_in_teu(
                vehicle=vehicle,
                container_counter=self._get_number_containers_for_outbound_journey,
            )
            self.occupied_capacity_for_outbound_journey_buffer[vehicle] = occupied_capacity_in_teu

        assert (
            unscaled_moved_container_volume - occupied_capacity_in_teu >= 0,
            f"vehicle {vehicle} is overloaded, "
            f"maximum_transported_container_volume: {maximum_transported_container_volume}, "
            f"unscaled_moved_container_volume: {unscaled_moved_container_volume}, "
            f"occupied_capacity_in_teu: {occupied_capacity_in_teu}"
        )

        free_capacity = max(maximum_transported_container_volume - occupied_capacity_in_teu, 0)

        return free_capacity

    @staticmethod
    def _get_occupied_capacity_in_teu(
            vehicle: Type[AbstractLargeScheduledVehicle],
            container_counter: Callable[[Type[AbstractLargeScheduledVehicle], ContainerLength], int],
    ) -> (float, float):
        loaded_20_foot_containers = container_counter(vehicle, ContainerLength.twenty_feet)
        loaded_40_foot_containers = container_counter(vehicle, ContainerLength.forty_feet)
        loaded_45_foot_containers = container_counter(vehicle, ContainerLength.forty_five_feet)
        loaded_other_containers = container_counter(vehicle, ContainerLength.other)
        occupied_capacity = (
                loaded_20_foot_containers * ContainerLength.get_teu_factor(ContainerLength.twenty_feet)
                + loaded_40_foot_containers * ContainerLength.get_teu_factor(ContainerLength.forty_feet)
                + loaded_45_foot_containers * ContainerLength.get_teu_factor(ContainerLength.forty_five_feet)
                + loaded_other_containers * ContainerLength.get_teu_factor(ContainerLength.other)
        )
        return occupied_capacity

    @classmethod
    def _get_number_containers_for_outbound_journey(
            cls,
            vehicle: Type[AbstractLargeScheduledVehicle],
            container_length: ContainerLength
    ) -> int:
        """Returns the number of containers on a specific vehicle of a specific container length that are picked up by
        the vehicle"""
        # noinspection PyTypeChecker
        large_scheduled_vehicle: LargeScheduledVehicle = vehicle.large_scheduled_vehicle
        number_loaded_containers = Container.select().where(
            (Container.picked_up_by_large_scheduled_vehicle == large_scheduled_vehicle)
            & (Container.length == container_length)
        ).count()
        return number_loaded_containers

    @classmethod
    def _get_number_containers_for_inbound_journey(
            cls,
            vehicle: AbstractLargeScheduledVehicle,
            container_length: ContainerLength
    ) -> int:
        """Returns the number of containers on a specific vehicle of a specific container length that are delivered by
        the vehicle"""

        large_scheduled_vehicle: LargeScheduledVehicle = vehicle.large_scheduled_vehicle
        number_loaded_containers = Container.select().where(
            (Container.delivered_by_large_scheduled_vehicle == large_scheduled_vehicle)
            & (Container.length == container_length)
        ).count()
        return number_loaded_containers
