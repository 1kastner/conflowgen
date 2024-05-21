from __future__ import annotations
import logging
from typing import Dict, Type, List

from conflowgen.application.repositories.random_seed_store_repository import get_initialised_random_object
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.factories.container_factory import ContainerFactory
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.repositories.large_scheduled_vehicle_repository import LargeScheduledVehicleRepository
from conflowgen.domain_models.vehicle import AbstractLargeScheduledVehicle


class AllocateSpaceForContainersDeliveredByTruckService:

    ignored_capacity = ContainerLength.get_teu_factor(ContainerLength.other)

    def __init__(self):
        self.seeded_random = get_initialised_random_object(self.__class__.__name__)

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
                         "trucks.")

    @staticmethod
    def _get_number_containers_to_allocate() -> int:
        """Create a balance between the number of containers which are picked up and which are delivered by truck.
        For most container terminals, these numbers are close to each other.

        As long as the container length distribution for inbound and outbound containers are the same, using the number
        of containers should lead to the same amount of containers as if we had taken the TEU capacity which is more
        complex to calculate.
        We do not consider the emergency pick-ups, i.e. the cases when a container was picked up by a truck just because
        no truck was available.
        These trucks artificially increase the import and export flows in case the container was originally a
        transshipment container and without this correction out of the sudden we have two containers in the yard.
        """
        number_containers: int = Container.select().where(
            (Container.picked_up_by == ModeOfTransport.truck)
            & ~Container.emergency_pickup
        ).count()
        return number_containers

    def allocate(self) -> None:
        """Allocates space for containers on vehicles that are delivered by trucks.
        """
        self.container_factory.reload_distributions()
        truck_to_other_vehicle_distribution: Dict[ModeOfTransport, float] = \
            self.mode_of_transport_distribution[ModeOfTransport.truck].copy()
        if truck_to_other_vehicle_distribution[ModeOfTransport.truck] > 0:
            raise NotImplementedError("Truck to truck traffic is not supported.")

        self.large_scheduled_vehicle_repository.reset_cache()

        number_containers_to_allocate = self._get_number_containers_to_allocate()

        # A list of vehicles that have free capacity for further containers. The entries are removed in a lazy fashion.
        vehicles: Dict[ModeOfTransport, List[Type[AbstractLargeScheduledVehicle]]]\
            = self.large_scheduled_vehicle_repository.load_all_vehicles()

        for vehicle_type, frequency in list(truck_to_other_vehicle_distribution.items()):
            if vehicle_type not in vehicles:  # this class is only concerned about large scheduled vehicles
                del truck_to_other_vehicle_distribution[vehicle_type]
                continue
            if frequency == 0:  # if the frequency is 0, we can ignore it right from the beginning and free resources
                del vehicles[vehicle_type]
                del truck_to_other_vehicle_distribution[vehicle_type]

        successful_assignment = 0

        teu_total = 0
        for i in range(1, number_containers_to_allocate + 1):
            if i % 1000 == 0 or i == 1 or i == number_containers_to_allocate:
                self.logger.info(
                    f"Progress: {i} / {number_containers_to_allocate} ({i / number_containers_to_allocate:.2%}) "
                    f"of the containers which are delivered by truck are allocated on a vehicle adhering to a schedule")
            while True:
                selected_mode_of_transport = self._pick_vehicle_type(truck_to_other_vehicle_distribution)

                # Ensure that if no storage space at all is left, this loop is aborted
                if selected_mode_of_transport is None:
                    self.logger.warning(
                        "No vehicles left at all! Aborting allocation process. "
                        f"This happened at container number {i} of {number_containers_to_allocate} (i.e., at "
                        f"{(i / number_containers_to_allocate * 100):.2f}%).")
                    return

                vehicles_of_type = vehicles[selected_mode_of_transport]

                # Ensure that if no vehicle of this type is left, this specific mode of transport is ignored
                if len(vehicles_of_type) == 0:
                    del truck_to_other_vehicle_distribution[selected_mode_of_transport]
                    self.logger.info(f"Vehicle type '{selected_mode_of_transport}' does not offer any capacities "
                                     f"anymore and is thus dropped. "
                                     f"This happened at container number {i} of {number_containers_to_allocate} (i.e., "
                                     f"at {(i / number_containers_to_allocate * 100):.2f}%).")
                    continue  # try again with another vehicle type (refers to while loop)

                vehicle = self._pick_vehicle(vehicles_of_type)

                if vehicle is None:
                    del truck_to_other_vehicle_distribution[selected_mode_of_transport]  # drop this type
                    continue  # try again with another vehicle type (refers to while loop)

                free_capacity_of_vehicle = self.large_scheduled_vehicle_repository.\
                    get_free_capacity_for_outbound_journey(vehicle, flow_direction="export")

                if free_capacity_of_vehicle <= self.ignored_capacity:

                    # noinspection PyTypeChecker
                    large_scheduled_vehicle: AbstractLargeScheduledVehicle = vehicle.large_scheduled_vehicle

                    large_scheduled_vehicle.capacity_exhausted_while_allocating_space_for_export_containers = True
                    large_scheduled_vehicle.save()

                    # Ignore the vehicle which would be overloaded if chosen
                    vehicles_of_type.remove(vehicle)

                    # noinspection PyTypeChecker
                    vehicle_name: str = large_scheduled_vehicle.vehicle_name

                    self.logger.debug(f"Vehicle '{vehicle_name}' of type '{selected_mode_of_transport}' has no "
                                      f"remaining capacity. The free capacity of {free_capacity_of_vehicle:.2f} "
                                      f"TEU is less than the required {self.ignored_capacity} TEU.")
                    continue  # try again (possibly new vehicle type, definitely not same vehicle again)

                container = self.container_factory.create_container_for_delivering_truck(vehicle)
                teu_total += ContainerLength.get_teu_factor(container.length)
                self.large_scheduled_vehicle_repository.block_capacity_for_outbound_journey(vehicle, container)
                successful_assignment += 1
                break  # success, no further looping to search for a suitable vehicle

        assert successful_assignment == number_containers_to_allocate, "Allocate all containers!"
        self.logger.info(f"All {successful_assignment} containers that need to be delivered by truck have been "
                         f"assigned to a vehicle that adheres to a schedule, corresponding to {teu_total} TEU.")

    def _pick_vehicle_type(
            self,
            truck_to_other_vehicle_distribution: dict[ModeOfTransport, float],
    ) -> ModeOfTransport | None:

        # Choose vehicle type according to distribution
        vehicle_types = list(truck_to_other_vehicle_distribution.keys())
        frequency_of_vehicle_types = list(truck_to_other_vehicle_distribution.values())

        sum_of_all_frequencies = sum(frequency_of_vehicle_types)
        if sum_of_all_frequencies == 0:
            self.logger.info("No vehicles are left for placing containers on them that are delivered by trucks.")
            return None

        # pick vehicle type
        vehicle_type: ModeOfTransport = self.seeded_random.choices(
            population=vehicle_types,
            weights=frequency_of_vehicle_types
        )[0]
        return vehicle_type

    def _pick_vehicle(
            self,
            vehicles_of_type: List[Type[AbstractLargeScheduledVehicle]]
    ) -> Type[AbstractLargeScheduledVehicle] | None:

        # Make it more likely that a container ends up on a large vessel than on a smaller one
        vehicle: Type[AbstractLargeScheduledVehicle]
        vehicle_distribution: Dict[Type[AbstractLargeScheduledVehicle], float] = {
            vehicle: self.large_scheduled_vehicle_repository.get_free_capacity_for_outbound_journey(vehicle)
            for vehicle in vehicles_of_type
        }
        all_free_capacities = list(vehicle_distribution.values())
        if sum(all_free_capacities) == 0:  # if there is no free vehicles left of a certain type...
            self.logger.info("No vehicles of selected type are left for placing containers on them that are delivered "
                             "by trucks.")
            return None

        vehicle: Type[AbstractLargeScheduledVehicle] = self.seeded_random.choices(
            population=list(vehicle_distribution.keys()),
            weights=list(vehicle_distribution.values())
        )[0]
        return vehicle
