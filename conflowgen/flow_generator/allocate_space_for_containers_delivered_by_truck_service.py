from __future__ import annotations
import logging
import random
from typing import Dict

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.factories.container_factory import ContainerFactory
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.repositories.large_scheduled_vehicle_repository import LargeScheduledVehicleRepository
from conflowgen.domain_models.vehicle import AbstractLargeScheduledVehicle


class AllocateSpaceForContainersDeliveredByTruckService:

    ignored_capacity = ContainerLength.get_factor(ContainerLength.other)

    def __init__(self):
        self.logger = logging.getLogger("conflowgen")
        self.mode_of_transport_distribution_repository = ModeOfTransportDistributionRepository()
        self.mode_of_transport_distribution: Dict[ModeOfTransport, Dict[ModeOfTransport, float]] | None = None
        self.large_scheduled_vehicle_repository = LargeScheduledVehicleRepository()
        self.container_factory = ContainerFactory()

    def reload_distribution(self, transportation_buffer: float):
        self.mode_of_transport_distribution = self.mode_of_transport_distribution_repository.get_distribution()
        self.large_scheduled_vehicle_repository.set_transportation_buffer(
            transportation_buffer=transportation_buffer
        )
        self.logger.info(f"Use transport buffer of {transportation_buffer} for allocating containers delivered by "
                         "trucks")

    @staticmethod
    def _get_number_containers_to_allocate() -> int:
        """Create a balance between the number of containers which are picked up and which are delivered by truck.
        For most container terminals, these numbers are close to each other.

        As long as the container length distribution for inbound and outbound containers are the same, using the number
        of containers should lead to the same amount of containers as if we had taken the TEU capacity which is more
        complex to calculate.
        """
        number_containers = Container.select().where(
            Container.picked_up_by == ModeOfTransport.truck
        ).count()
        return number_containers

    def allocate(self) -> None:
        """Allocates space for containers on vehicles that are delivered by trucks.
        """
        self.container_factory.reload_distributions()
        truck_to_other_vehicle_distribution: Dict[ModeOfTransport, float] = \
            self.mode_of_transport_distribution[ModeOfTransport.truck].copy()
        if truck_to_other_vehicle_distribution[ModeOfTransport.truck] > 0:
            raise NotImplementedError()

        self.large_scheduled_vehicle_repository.reset_cache()

        number_containers_to_allocate = self._get_number_containers_to_allocate()

        # A list of vehicles that have free capacity for further containers. The entries are removed in a lazy fashion.
        vehicles = self.large_scheduled_vehicle_repository.load_all_vehicles()

        for vehicle_type, frequency in list(truck_to_other_vehicle_distribution.items()):
            if vehicle_type not in vehicles:  # this class is only concerned about large scheduled vehicles
                del truck_to_other_vehicle_distribution[vehicle_type]
                continue
            if frequency == 0:  # if the frequency is 0, we can ignore it right from the beginning and free resources
                del vehicles[vehicle_type]
                del truck_to_other_vehicle_distribution[vehicle_type]

        abort = False

        for i in range(number_containers_to_allocate):
            i += 1
            if i % 1000 == 0 and i > 0:
                self.logger.info(
                    f"Progress: {i} / {number_containers_to_allocate} ({100 * i / number_containers_to_allocate:.2f}%) "
                    f"of the containers which are delivered by truck are allocated on a vehicle adhering to a schedule")
            while True:
                # Choose vehicle type according to distribution
                vehicle_types = list(truck_to_other_vehicle_distribution.keys())
                frequency_of_vehicle_types = list(truck_to_other_vehicle_distribution.values())

                # rescale so that all values sum up to one
                sum_of_all_frequencies = sum(frequency_of_vehicle_types)
                if sum_of_all_frequencies == 0:
                    self.logger.info("No vehicles are left for placing containers on them that are delivered by "
                                     f"trucks. This happened at container number {i} of "
                                     f"{number_containers_to_allocate} (i.e., at "
                                     f"{(i / number_containers_to_allocate * 100):.2f}%).")
                    abort = True  # is used to break eternal looping at the end of the for loop
                    break  # Not enough vehicles of any kind could be found (refers to while loop)
                frequency_of_vehicle_types = [
                    i / sum_of_all_frequencies
                    for i in frequency_of_vehicle_types
                ]

                # pick vehicle type
                vehicle_type: ModeOfTransport = random.choices(
                    population=vehicle_types,
                    weights=frequency_of_vehicle_types
                )[0]
                vehicles_of_type = vehicles[vehicle_type]
                if len(vehicles_of_type) == 0:  # Ensure that if no vehicle is left, this mode of transport is ignored
                    del truck_to_other_vehicle_distribution[vehicle_type]
                    self.logger.info(f"Vehicle type '{vehicle_type}' is exhausted and is no further tried. This "
                                     f"happened at container number {i} of {number_containers_to_allocate} (i.e., "
                                     f"at {(i / number_containers_to_allocate * 100):.2f}%).")
                    continue  # try again with another vehicle type (refers to while loop)

                # Make it more likely that a container ends up on a large vessel than on a smaller one
                vehicle_distribution = {
                    vehicle: self.large_scheduled_vehicle_repository.get_free_capacity_for_outbound_journey(vehicle)
                    for vehicle in vehicles_of_type
                }
                all_free_capacities = list(vehicle_distribution.values())
                if sum(all_free_capacities) == 0:  # if there is no free vehicles left of a certain type...
                    del truck_to_other_vehicle_distribution[vehicle_type]   # drop this type and...
                    continue  # try again
                vehicle: AbstractLargeScheduledVehicle = random.choices(
                    population=list(vehicle_distribution.keys()),
                    weights=list(vehicle_distribution.values())
                )[0]

                free_capacity_of_vehicle = self.large_scheduled_vehicle_repository.\
                    get_free_capacity_for_outbound_journey(vehicle)
                if free_capacity_of_vehicle <= self.ignored_capacity:
                    large_scheduled_vehicle: AbstractLargeScheduledVehicle = vehicle.large_scheduled_vehicle
                    large_scheduled_vehicle.capacity_exhausted_while_allocating_space_for_export_containers = True
                    large_scheduled_vehicle.save()
                    vehicles_of_type.remove(vehicle)  # Ignore the vehicle which would be overloaded if chosen
                    vehicle_name: str = vehicle.large_scheduled_vehicle.vehicle_name
                    self.logger.debug(f"Vehicle '{vehicle_name}' of type '{vehicle_type}' has no remaining capacity "
                                      f"and is no further tried - free capacity of {free_capacity_of_vehicle:.2f} "
                                      f"TEU is less than the required {self.ignored_capacity} TEU.")
                    continue  # try again (possibly new vehicle type, definitely not same vehicle again)

                container = self.container_factory.create_container_for_delivering_truck(vehicle)
                self.large_scheduled_vehicle_repository.block_capacity_for_outbound_journey(vehicle, container)
                break  # success, no further looping to search for a suitable vehicle

            if abort:  # Not enough vehicles of any kind could be found
                break  # break out of for loop

        self.logger.info("All containers that need to be delivered by truck have been assigned to a vehicle that moves "
                         "according to a schedule.")
