import datetime
import typing
from typing import List, Type
import logging

from conflowgen.application.services.vehicle_capacity_manager import VehicleCapacityManager
from conflowgen.descriptive_datatypes import FlowDirection
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.repositories.large_scheduled_vehicle_repository import LargeScheduledVehicleRepository
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, AbstractLargeScheduledVehicle


class ScheduleRepository:

    def __init__(self):
        self.logger = logging.getLogger("conflowgen")
        self.large_scheduled_vehicle_repository = LargeScheduledVehicleRepository()
        self.vehicle_capacity_manager = VehicleCapacityManager()

    def set_transportation_buffer(self, transportation_buffer: float):
        self.vehicle_capacity_manager.set_transportation_buffer(transportation_buffer)

    def set_ramp_up_and_down_times(
            self,
            ramp_up_period_end: typing.Optional[datetime.datetime] = None,
            ramp_down_period_start: typing.Optional[datetime.datetime] = None
    ):
        self.vehicle_capacity_manager.set_ramp_up_and_down_times(
            ramp_up_period_end=ramp_up_period_end,
            ramp_down_period_start=ramp_down_period_start
        )

    def get_departing_vehicles(
            self,
            start: datetime.datetime,
            end: datetime.datetime,
            vehicle_type: ModeOfTransport,
            required_capacity: ContainerLength,
            flow_direction: FlowDirection
    ) -> List[Type[AbstractLargeScheduledVehicle]]:
        """Gets the available vehicles for the required capacity of the required type and within the time range.
        """
        assert start <= end

        # Get type, i.e. Feeder, DeepSeaVessel, etc.
        large_scheduled_vehicle_as_subtype = AbstractLargeScheduledVehicle.map_mode_of_transport_to_class(
            vehicle_type
        )

        # Get all vehicles in the time range
        vehicles = large_scheduled_vehicle_as_subtype.select().join(LargeScheduledVehicle).where(
            (large_scheduled_vehicle_as_subtype.large_scheduled_vehicle.scheduled_arrival >= start)
            & (large_scheduled_vehicle_as_subtype.large_scheduled_vehicle.scheduled_arrival <= end)
        )

        # Check for each of the vehicles how much it has already loaded
        required_capacity_in_teu = ContainerLength.get_teu_factor(required_capacity)
        vehicles_with_sufficient_capacity = []
        vehicle: Type[AbstractLargeScheduledVehicle]
        for vehicle in vehicles:
            free_capacity_in_teu = self.vehicle_capacity_manager.\
                get_free_capacity_for_outbound_journey(
                    vehicle, flow_direction
                )

            if free_capacity_in_teu >= required_capacity_in_teu:
                vehicles_with_sufficient_capacity.append(vehicle)
            assert free_capacity_in_teu >= 0, f"Vehicle {vehicle} is overloaded, checking for " \
                                              f"start: {start}, end: {end}, vehicle_type: {vehicle_type}, " \
                                              f"required capacity in TEU: {required_capacity_in_teu} " \
                                              f"but free capacity in TEU: {free_capacity_in_teu}"

        return vehicles_with_sufficient_capacity

    def block_capacity_for_outbound_journey(
            self,
            vehicle: Type[AbstractLargeScheduledVehicle],
            container: Container,
    ) -> bool:
        """Updates the cache for faster execution
        """
        return self.vehicle_capacity_manager.block_capacity_for_outbound_journey(
            vehicle=vehicle,
            container=container
        )
