from __future__ import annotations
import datetime
import logging
import math
import random
from typing import Collection, Tuple, List, Dict, Type, Sequence

from peewee import fn

from ..domain_models.data_types.container_length import ContainerLength
from ..domain_models.data_types.storage_requirement import StorageRequirement
from ..domain_models.arrival_information import TruckArrivalInformationForDelivery
from ..domain_models.container import Container
from ..domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from ..domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..domain_models.repositories.schedule_repository import ScheduleRepository
from ..domain_models.vehicle import AbstractLargeScheduledVehicle, LargeScheduledVehicle, Truck
from ..tools.continuous_distribution import ContinuousDistribution, multiply_discretized_probability_densities


class LargeScheduledVehicleForOnwardTransportationManager:

    random_seed = 1

    def __init__(self):
        self.seeded_random = random.Random(x=self.random_seed)
        self.logger = logging.getLogger("conflowgen")
        self.schedule_repository = ScheduleRepository()
        self.large_scheduled_vehicle_repository = self.schedule_repository.large_scheduled_vehicle_repository
        self.mode_of_transport_distribution_repository = ModeOfTransportDistributionRepository()
        self.mode_of_transport_distribution = self.mode_of_transport_distribution_repository.get_distribution()
        self.number_assigned_containers = 0
        self.number_not_assignable_containers = 0

        self.container_dwell_time_distribution_repository = ContainerDwellTimeDistributionRepository()
        self.container_dwell_time_distributions: \
            Dict[ModeOfTransport, Dict[ModeOfTransport, Dict[StorageRequirement, ContinuousDistribution]]] | None \
            = None

    def reload_properties(
            self,
            transportation_buffer: float
    ):
        assert -1 < transportation_buffer
        self.schedule_repository.set_transportation_buffer(transportation_buffer)
        self.logger.debug(f"Using transportation buffer of {transportation_buffer} when choosing the departing "
                          f"vehicles that adhere a schedule.")

        self.container_dwell_time_distributions = self.container_dwell_time_distribution_repository.get_distributions()
        self.large_scheduled_vehicle_repository = self.schedule_repository.large_scheduled_vehicle_repository
        self.mode_of_transport_distribution = self.mode_of_transport_distribution_repository.get_distribution()

    def choose_departing_vehicle_for_containers(self) -> None:
        """For all containers that are already in the database and that continue their journey with a vehicle that
        moves according to a schedule, a suiting vehicle is assigned here.

        Currently, first containers are delivered by vehicles that move according to a schedule. The containers that
        are delivered by truck are handled later on.

        This method might be quite time-consuming because it repeatedly checks how many containers are already placed
        on a vehicle to obey the load restriction (maximum capacity of the vehicle available for the terminal).
        """
        self.number_assigned_containers = 0
        self.number_not_assignable_containers = 0

        self.large_scheduled_vehicle_repository.reset_cache()

        self.logger.info("Assign containers to departing vehicles that move according to a schedule...")

        # Get all containers in a random order which are picked up by a LargeScheduledVehicle
        # This way no vehicle has an advantage over another by its earlier arrival (getting better slots etc.)
        containers: Collection[Container] = Container.select(
        ).order_by(fn.Random()).where(
            Container.picked_up_by << ModeOfTransport.get_scheduled_vehicles()
        )  # TODO: add joins here to avoid that many database look-ups later

        self.logger.info(f"In total {len(containers)} containers continue their journey on a vehicle that adhere to a "
                         f"schedule, assigning these containers to their respective vehicles...")
        for i, container in enumerate(containers):
            i += 1
            if i % 1000 == 0 and i > 0:
                self.logger.info(f"Progress: {i} / {len(containers)} ({100 * i / len(containers):.2f}%) "
                                 f"containers have been assigned to a scheduled vehicle to leave the terminal again.")

            container_arrival = self._get_arrival_time_of_container(container)

            minimum_dwell_time_in_hours, maximum_dwell_time_in_hours = self._get_dwell_times(container)

            # This value has been randomly drawn during container generation for the inbound traffic.
            # We try to adhere to that value as well as possible.
            initial_departing_vehicle_type = container.picked_up_by_initial

            # Get all vehicles which could be used for the onward transportation of the container
            available_vehicles = self.schedule_repository.get_departing_vehicles(
                start=(container_arrival + datetime.timedelta(hours=minimum_dwell_time_in_hours)),
                end=(container_arrival + datetime.timedelta(hours=maximum_dwell_time_in_hours)),
                vehicle_type=initial_departing_vehicle_type,
                required_capacity=container.length
            )

            if len(available_vehicles) > 0:
                # this is the case when there is a vehicle available - let's hope everything else works out as well!
                vehicle = self._pick_vehicle_for_container(available_vehicles, container)
                if vehicle is not None:
                    self.number_assigned_containers += 1
                else:
                    # Well, there was a vehicle available. However, it was not suitable for our container due to
                    # some constraint. Maybe the container dwell time was unrealistic and thus not permissible?
                    # This can happen if the distribution is just really, really close to zero, so it is approximated
                    # as zero.
                    self.number_not_assignable_containers += 1
                    self._find_alternative_mode_of_transportation(
                        container, container_arrival, minimum_dwell_time_in_hours, maximum_dwell_time_in_hours
                    )
            else:
                # Maybe no permissible vehicles of the required vehicle type are left, then we need to switch the type
                # as to somehow move the container out of the container yard.
                self.number_not_assignable_containers += 1
                self._find_alternative_mode_of_transportation(
                    container, container_arrival, minimum_dwell_time_in_hours, maximum_dwell_time_in_hours
                )

        self.logger.info("All containers for which a departing vehicle that moves according to a schedule was "
                         "available have been assigned to one.")

    def _pick_vehicle_for_container(
            self,
            available_vehicles: List[Type[AbstractLargeScheduledVehicle]],
            container: Container
    ) -> Type[AbstractLargeScheduledVehicle] | None:
        """It is ensured that at least one vehicle is available
        """
        vehicle = self._draw_vehicle(available_vehicles, container)
        if vehicle is not None:
            self._save_chosen_vehicle(container, vehicle)
        return vehicle

    def _save_chosen_vehicle(self, container, vehicle):
        large_scheduled_vehicle: LargeScheduledVehicle = vehicle.large_scheduled_vehicle
        vehicle_type = vehicle.get_mode_of_transport()
        container.picked_up_by_large_scheduled_vehicle = large_scheduled_vehicle
        container.picked_up_by = vehicle_type
        container.save()
        vehicle_capacity_is_exhausted = self.schedule_repository.block_capacity_for_outbound_journey(vehicle, container)
        if vehicle_capacity_is_exhausted:
            large_scheduled_vehicle.capacity_exhausted_while_determining_onward_transportation = True
            large_scheduled_vehicle.save()

    def _draw_vehicle(
            self,
            available_vehicles: Sequence[Type[LargeScheduledVehicle]],
            container: Container
    ) -> Type[AbstractLargeScheduledVehicle] | None:
        assert len(available_vehicles) > 0, "Some vehicle is available to take the container on its outbound journey " \
                                            "within the assumed container dwell time (min < x < max)."
        if len(available_vehicles) == 1:
            return available_vehicles[0]

        vehicles_and_their_respective_free_capacity = {}
        for vehicle in available_vehicles:
            free_capacity = self.large_scheduled_vehicle_repository.get_free_capacity_for_outbound_journey(vehicle)
            if free_capacity >= ContainerLength.get_factor(ContainerLength.other):
                vehicles_and_their_respective_free_capacity[vehicle] = free_capacity

        # drop those vehicles without free capacities, they are not really available
        available_vehicles = list(vehicles_and_their_respective_free_capacity.keys())
        free_capacities = list(vehicles_and_their_respective_free_capacity.values())

        container_arrival = self._get_arrival_time_of_container(container)
        associated_dwell_times = []
        for vehicle in available_vehicles:
            # noinspection PyUnresolvedReferences
            vehicle_departure_date: datetime.datetime = vehicle.large_scheduled_vehicle.scheduled_arrival
            dwell_time_if_vehicle_is_chosen = vehicle_departure_date - container_arrival
            dwell_time_if_vehicle_is_chosen_in_hours = dwell_time_if_vehicle_is_chosen.total_seconds() / 3600
            associated_dwell_times.append(dwell_time_if_vehicle_is_chosen_in_hours)
        container_dwell_time_distribution = self._get_container_dwell_time_distribution(
            container.delivered_by, container.picked_up_by, container.storage_requirement
        )
        container_dwell_time_probabilities = container_dwell_time_distribution.get_probabilities(associated_dwell_times)
        total_probabilities = multiply_discretized_probability_densities(
            free_capacities,
            container_dwell_time_probabilities
        )
        vehicles_and_their_respective_probability = {
            vehicle: probability
            for vehicle, probability in zip(available_vehicles, total_probabilities)
            if probability > 0
        }
        if len(vehicles_and_their_respective_probability):
            vehicle: Type[AbstractLargeScheduledVehicle] = self.seeded_random.choices(
                population=list(vehicles_and_their_respective_probability.keys()),
                weights=list(vehicles_and_their_respective_probability.values())
            )[0]
            return vehicle
        return None  # No suitable vehicle could be found

    def _get_dwell_times(self, container: Container) -> Tuple[int, int]:
        """get correct dwell time depending on transportation mode.
        """

        distribution = self.container_dwell_time_distributions[container.delivered_by][container.picked_up_by][
            container.storage_requirement]

        minimum_dwell_time_in_hours = int(math.ceil(distribution.minimum))
        maximum_dwell_time_in_hours = int(math.floor(distribution.maximum))

        return minimum_dwell_time_in_hours, maximum_dwell_time_in_hours

    @staticmethod
    def _get_arrival_time_of_container(container: Container) -> datetime.datetime:
        """get container arrival from correct source
        """
        container_arrival: datetime.datetime
        if container.delivered_by == ModeOfTransport.truck:
            truck: Truck = container.delivered_by_truck
            truck_arrival_information: TruckArrivalInformationForDelivery = truck.truck_arrival_information_for_delivery
            container_arrival = truck_arrival_information.realized_container_delivery_time
        else:
            large_scheduled_vehicle: LargeScheduledVehicle = container.delivered_by_large_scheduled_vehicle
            container_arrival = large_scheduled_vehicle.scheduled_arrival
        return container_arrival

    @staticmethod
    def _get_departure_time_of_vehicle(
            vehicle: Truck | Type[AbstractLargeScheduledVehicle]
    ) -> datetime.datetime:
        """get container arrival from correct source
        """
        vehicle_departure: datetime.datetime
        if isinstance(vehicle, Truck):
            truck_arrival_information: TruckArrivalInformationForDelivery = \
                vehicle.truck_arrival_information_for_delivery
            vehicle_departure = truck_arrival_information.planned_container_delivery_time_at_window_start
        elif isinstance(vehicle, AbstractLargeScheduledVehicle):
            vehicle_departure = vehicle.scheduled_arrival
        else:
            raise Exception(f"Unknown type {type(vehicle)} of vehicle {vehicle}.")
        return vehicle_departure

    def _find_alternative_mode_of_transportation(
            self,
            container: Container,
            container_arrival: datetime.datetime,
            minimum_dwell_time_in_hours: float,
            maximum_dwell_time_in_hours: float,
    ):
        # It should be clear anyway that this container had to change its vehicle
        container.emergency_pickup = True

        # These are the default values if no suitable vehicle could be found in the next lines
        container.picked_up_by = ModeOfTransport.truck
        container.save()

        # get alternative vehicles
        vehicle_types_and_their_fraction = self.mode_of_transport_distribution[container.delivered_by].copy()

        # ignore the one vehicle type which has obviously failed, otherwise we wouldn't search for an alternative here
        previous_failed_vehicle_type: ModeOfTransport = container.picked_up_by
        del vehicle_types_and_their_fraction[previous_failed_vehicle_type]

        # try to pick a better vehicle for 5 times, otherwise the previously set default values are automatically used
        for _ in range(5):
            if len(vehicle_types_and_their_fraction) == 0:
                # All vehicles of the vehicle type(s) that are available for a given container type lack free capacity.
                # A default value has been pre-selected anyway a bit earlier, nothing else to do.
                return

            fractions = list(vehicle_types_and_their_fraction.values())

            if sum(fractions) == 0:
                # Only those vehicle types are left that cannot pick up the container in question.
                # A default value has been pre-selected anyway a bit earlier, nothing else to do.
                return

            # Drop fractions of 0 because the random module cannot digest them properly
            updated_vehicle_types_and_frequencies = {
                vehicle_type: fraction
                for vehicle_type, fraction in vehicle_types_and_their_fraction.items()
                if 0 < fraction
            }

            vehicle_type = self.seeded_random.choices(
                population=list(updated_vehicle_types_and_frequencies.keys()),
                weights=list(updated_vehicle_types_and_frequencies.values())
            )[0]

            if vehicle_type == ModeOfTransport.truck:
                # This default value has been pre-selected anyway, nothing else to do.
                return

            available_vehicles = self.schedule_repository.get_departing_vehicles(
                start=(container_arrival + datetime.timedelta(hours=minimum_dwell_time_in_hours)),
                end=(container_arrival + datetime.timedelta(hours=maximum_dwell_time_in_hours)),
                vehicle_type=vehicle_type,
                required_capacity=container.length
            )
            if len(available_vehicles) > 0:  # There is a vehicle of a new type available, so it is picked
                vehicle = self._pick_vehicle_for_container(available_vehicles, container)
                if vehicle is None:
                    # Well, there was a vehicle available. However, it was not suitable for our container due to
                    # some constraint. Maybe the container dwell time was unrealistic and thus forbidden?
                    # This can happen if the distribution is just really, really close to zero, so it is approximated
                    # as zero.
                    del vehicle_types_and_their_fraction[vehicle_type]
                    continue
                else:
                    return

            # There is no vehicles of this type are left either, so it should also be excluded from the random
            # selection procedure to reduce the noise (weights of zero).
            del vehicle_types_and_their_fraction[vehicle_type]

    def _get_container_dwell_time_distribution(
            self,
            inbound_vehicle: ModeOfTransport,
            outbound_vehicle: ModeOfTransport,
            storage_requirement: StorageRequirement
    ) -> ContinuousDistribution:
        return self.container_dwell_time_distributions[inbound_vehicle][outbound_vehicle][storage_requirement]
