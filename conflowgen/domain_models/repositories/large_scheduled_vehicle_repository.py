import datetime
import enum
import logging
import typing
from typing import Dict, List, Callable, Type

from conflowgen.descriptive_datatypes import FlowDirection
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, AbstractLargeScheduledVehicle


class JourneyDirection(enum.Enum):
    inbound = "inbound"
    outbound = "outbound"


class LargeScheduledVehicleRepository:

    ignored_capacity = ContainerLength.get_teu_factor(ContainerLength.other)

    downscale_factor_during_ramp_up_for_outbound_transshipment = 0.1

    downscale_factor_during_ramp_down_for_inbound_all_kinds = 0.1

    def __init__(self):
        self.transportation_buffer = None
        self.ramp_up_period_end = None
        self.ramp_down_period_start = None
        self.free_capacity_for_outbound_journey_buffer: Dict[Type[AbstractLargeScheduledVehicle], float] = {}
        self.free_capacity_for_inbound_journey_buffer: Dict[Type[AbstractLargeScheduledVehicle], float] = {}
        self.logger = logging.getLogger("conflowgen")

    def set_transportation_buffer(self, transportation_buffer: float):
        assert -1 < transportation_buffer
        self.transportation_buffer = transportation_buffer

    def set_ramp_up_and_down_times(
            self,
            ramp_up_period_end: typing.Optional[datetime.datetime] = None,
            ramp_down_period_start: typing.Optional[datetime.datetime] = None
    ) -> None:
        self.ramp_up_period_end = ramp_up_period_end
        self.ramp_down_period_start = ramp_down_period_start

    def reset_cache(self):
        self.free_capacity_for_outbound_journey_buffer = {}
        self.free_capacity_for_inbound_journey_buffer = {}

    @staticmethod
    def load_all_vehicles() -> Dict[ModeOfTransport, List[Type[AbstractLargeScheduledVehicle]]]:
        result = {}
        for vehicle_type in ModeOfTransport.get_scheduled_vehicles():
            large_schedule_vehicle_as_subtype = AbstractLargeScheduledVehicle.map_mode_of_transport_to_class(
                vehicle_type)
            result[vehicle_type] = list(large_schedule_vehicle_as_subtype.select().join(LargeScheduledVehicle))
        return result

    def block_capacity_for_inbound_journey(
            self,
            vehicle: Type[AbstractLargeScheduledVehicle],
            container: Container
    ) -> bool:
        assert vehicle in self.free_capacity_for_inbound_journey_buffer, \
            "First .get_free_capacity_for_inbound_journey(vehicle) must be invoked"

        # calculate new free capacity
        free_capacity_in_teu = self.free_capacity_for_inbound_journey_buffer[vehicle]
        used_capacity_in_teu = ContainerLength.get_teu_factor(container_length=container.length)
        new_free_capacity_in_teu = free_capacity_in_teu - used_capacity_in_teu
        assert new_free_capacity_in_teu >= 0, f"vehicle {vehicle} is overloaded, " \
                                              f"free_capacity_in_teu: {free_capacity_in_teu}, " \
                                              f"used_capacity_in_teu: {used_capacity_in_teu}, " \
                                              f"new_free_capacity_in_teu: {new_free_capacity_in_teu}"

        self.free_capacity_for_inbound_journey_buffer[vehicle] = new_free_capacity_in_teu
        vehicle_capacity_is_exhausted = new_free_capacity_in_teu < self.ignored_capacity
        return vehicle_capacity_is_exhausted

    def block_capacity_for_outbound_journey(
            self,
            vehicle: Type[AbstractLargeScheduledVehicle],
            container: Container
    ) -> bool:
        assert vehicle in self.free_capacity_for_outbound_journey_buffer, \
            "First .get_free_capacity_for_outbound_journey(vehicle) must be invoked"

        # calculate new free capacity
        free_capacity_in_teu = self.free_capacity_for_outbound_journey_buffer[vehicle]
        used_capacity_in_teu = ContainerLength.get_teu_factor(container_length=container.length)
        new_free_capacity_in_teu = free_capacity_in_teu - used_capacity_in_teu
        assert new_free_capacity_in_teu >= 0, f"vehicle {vehicle} is overloaded, " \
                                              f"free_capacity_in_teu: {free_capacity_in_teu}, " \
                                              f"used_capacity_in_teu: {used_capacity_in_teu}, " \
                                              f"new_free_capacity_in_teu: {new_free_capacity_in_teu}"

        self.free_capacity_for_outbound_journey_buffer[vehicle] = new_free_capacity_in_teu
        return new_free_capacity_in_teu <= self.ignored_capacity

    # noinspection PyTypeChecker
    def get_free_capacity_for_inbound_journey(self, vehicle: Type[AbstractLargeScheduledVehicle]) -> float:
        """
        Get the free capacity for the inbound journey on a vehicle that moves according to a schedule in TEU.
        During the ramp-down period (if existent), all inbound traffic is scaled down, no matter what.
        """
        if vehicle in self.free_capacity_for_inbound_journey_buffer:
            return self.free_capacity_for_inbound_journey_buffer[vehicle]

        large_scheduled_vehicle: LargeScheduledVehicle = vehicle.large_scheduled_vehicle
        total_moved_capacity_for_inbound_transportation_in_teu = large_scheduled_vehicle.moved_capacity
        factored_free_capacity_in_teu, free_capacity_in_teu = self._get_free_capacity_in_teu(
            vehicle=vehicle,
            maximum_capacity=total_moved_capacity_for_inbound_transportation_in_teu,
            container_counter=self._get_number_containers_for_inbound_journey,
            journey_direction=JourneyDirection.inbound,
            flow_direction=FlowDirection.undefined
        )
        self.free_capacity_for_inbound_journey_buffer[vehicle] = factored_free_capacity_in_teu
        return factored_free_capacity_in_teu

    def get_free_capacity_for_outbound_journey(
            self, vehicle: Type[AbstractLargeScheduledVehicle],
            flow_direction: FlowDirection
    ) -> float:
        """
        Get the free capacity for the outbound journey on a vehicle that moves according to a schedule in TEU.
        During the ramp-up period (if existent), all outbound traffic that constitutes transshipment, is scaled down.
        """
        assert self.transportation_buffer is not None, "First set the value!"
        assert -1 < self.transportation_buffer, "Must be larger than -1"

        if vehicle in self.free_capacity_for_outbound_journey_buffer:
            if flow_direction == FlowDirection.transshipment_flow and self.ramp_up_period_end is not None:

                # noinspection PyUnresolvedReferences
                arrival_time: datetime.datetime = vehicle.large_scheduled_vehicle.scheduled_arrival

                if arrival_time < self.ramp_up_period_end:
                    return (  # factored capacity
                            self.free_capacity_for_outbound_journey_buffer[vehicle]
                            * self.downscale_factor_during_ramp_up_for_outbound_transshipment
                    )
            # capacity without factor
            return self.free_capacity_for_outbound_journey_buffer[vehicle]

        # if not yet buffered:

        # noinspection PyTypeChecker
        large_scheduled_vehicle: LargeScheduledVehicle = vehicle.large_scheduled_vehicle

        total_moved_capacity_for_onward_transportation_in_teu = \
            large_scheduled_vehicle.moved_capacity * (1 + self.transportation_buffer)
        maximum_capacity_of_vehicle = large_scheduled_vehicle.capacity_in_teu
        total_moved_capacity_for_onward_transportation_in_teu = min(
            total_moved_capacity_for_onward_transportation_in_teu,
            maximum_capacity_of_vehicle
        )

        factored_free_capacity_in_teu, free_capacity_in_teu = self._get_free_capacity_in_teu(
            vehicle=vehicle,
            maximum_capacity=total_moved_capacity_for_onward_transportation_in_teu,
            container_counter=self._get_number_containers_for_outbound_journey,
            journey_direction=JourneyDirection.outbound,
            flow_direction=flow_direction
        )

        # always cache the free capacity without a factor, as it only applies in some situations
        self.free_capacity_for_outbound_journey_buffer[vehicle] = free_capacity_in_teu

        # always report the factored capacity to the user of this class
        return factored_free_capacity_in_teu

    def _get_free_capacity_in_teu(
            self,
            vehicle: Type[AbstractLargeScheduledVehicle],
            maximum_capacity: int,
            container_counter: Callable[[Type[AbstractLargeScheduledVehicle], ContainerLength], int],
            journey_direction: JourneyDirection,
            flow_direction: FlowDirection
    ) -> (float, float):
        loaded_20_foot_containers = container_counter(vehicle, ContainerLength.twenty_feet)
        loaded_40_foot_containers = container_counter(vehicle, ContainerLength.forty_feet)
        loaded_45_foot_containers = container_counter(vehicle, ContainerLength.forty_five_feet)
        loaded_other_containers = container_counter(vehicle, ContainerLength.other)
        free_capacity_in_teu = (
                maximum_capacity
                - loaded_20_foot_containers * ContainerLength.get_teu_factor(ContainerLength.twenty_feet)
                - loaded_40_foot_containers * ContainerLength.get_teu_factor(ContainerLength.forty_feet)
                - loaded_45_foot_containers * ContainerLength.get_teu_factor(ContainerLength.forty_five_feet)
                - loaded_other_containers * ContainerLength.get_teu_factor(ContainerLength.other)
        )

        # noinspection PyUnresolvedReferences
        vehicle_name = vehicle.large_scheduled_vehicle.vehicle_name

        assert free_capacity_in_teu >= 0, f"vehicle {vehicle} of type {vehicle.get_mode_of_transport()} with the " \
                                          f"name '{vehicle_name}' " \
                                          f"is overloaded, " \
                                          f"free_capacity_in_teu: {free_capacity_in_teu} with " \
                                          f"maximum_capacity: {maximum_capacity}, " \
                                          f"loaded_20_foot_containers: {loaded_20_foot_containers}, " \
                                          f"loaded_40_foot_containers: {loaded_40_foot_containers}, " \
                                          f"loaded_45_foot_containers: {loaded_45_foot_containers} and " \
                                          f"loaded_other_containers: {loaded_other_containers}"

        # noinspection PyUnresolvedReferences
        arrival_time: datetime.datetime = vehicle.large_scheduled_vehicle.scheduled_arrival

        factored_free_capacity_in_teu = free_capacity_in_teu

        if (
                journey_direction == JourneyDirection.outbound
                and flow_direction == FlowDirection.transshipment_flow
                and self.ramp_up_period_end is not None
                and arrival_time < self.ramp_up_period_end
        ):
            # keep transshipment containers in the yard longer during the ramp-up period to fill the yard faster
            # by offering less transport capacity on the outbound journey of deep sea vessels and feeders
            factored_free_capacity_in_teu = (
                    free_capacity_in_teu * self.downscale_factor_during_ramp_up_for_outbound_transshipment
            )

        elif (
                journey_direction == JourneyDirection.inbound
                and self.ramp_down_period_start is not None
                and arrival_time >= self.ramp_down_period_start
        ):
            # decrease number of inbound containers (any direction) during the ramp-down period
            # by offering less transport capacity on the inbound journey (all types of vehicles, excluding trucks)
            factored_free_capacity_in_teu = (
                    free_capacity_in_teu * self.downscale_factor_during_ramp_down_for_inbound_all_kinds
            )

        return factored_free_capacity_in_teu, free_capacity_in_teu

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
