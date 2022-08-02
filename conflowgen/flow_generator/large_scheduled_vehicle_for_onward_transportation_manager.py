from __future__ import annotations
import datetime
import logging
import math
import random
from typing import Collection, Tuple, List, Dict, Any

from peewee import fn

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

    def __init__(self):
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
        )

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
                # this is the case when there is a vehicle available, and we can assign the container to that vehicle
                # which is the happy path
                self.number_assigned_containers += 1
                self._pick_vehicle_for_container(available_vehicles, container)
            else:
                # maybe no possible vehicles are left of the required vehicle type, then we need to switch if we want to
                # get the container out of the container yard before storage fees apply
                self.number_not_assignable_containers += 1
                self._find_alternative_mode_of_transportation(
                    container, container_arrival, minimum_dwell_time_in_hours, maximum_dwell_time_in_hours
                )

        self.logger.info("All containers for which a departing vehicle that moves according to a schedule was "
                         "available have been assigned to one.")

    def _pick_vehicle_for_container(
            self,
            available_vehicles: List[AbstractLargeScheduledVehicle],
            container: Container
    ) -> AbstractLargeScheduledVehicle:
        """Pick vehicle with the probability of its free capacity
        """
        vehicle_availability = {
            vehicle: self.large_scheduled_vehicle_repository.get_free_capacity_for_outbound_journey(vehicle)
            for vehicle in available_vehicles
        }
        available_vehicles = list(vehicle_availability.keys())

        container_arrival = self._get_arrival_time_of_container(container)
        associated_dwell_times = []
        for vehicle in available_vehicles:
            vehicle_departure_date: datetime.datetime = vehicle.large_scheduled_vehicle.scheduled_arrival
            dwell_time_if_vehicle_is_chosen = vehicle_departure_date - container_arrival
            dwell_time_if_vehicle_is_chosen_in_hours = dwell_time_if_vehicle_is_chosen.total_seconds() / 3600
            associated_dwell_times.append(dwell_time_if_vehicle_is_chosen_in_hours)

        container_dwell_time_distribution = self._get_container_dwell_time_distribution(
            container.delivered_by, container.picked_up_by, container.storage_requirement
        )
        container_dwell_time_probabilities = container_dwell_time_distribution.get_probabilities(associated_dwell_times)
        total_probabilities = multiply_discretized_probability_densities(
            associated_dwell_times,
            container_dwell_time_probabilities
        )

        vehicle: AbstractLargeScheduledVehicle = random.choices(
            population=available_vehicles,
            weights=total_probabilities
        )[0]
        large_scheduled_vehicle: LargeScheduledVehicle = vehicle.large_scheduled_vehicle
        vehicle_type = vehicle.get_mode_of_transport()

        container.picked_up_by_large_scheduled_vehicle = large_scheduled_vehicle
        container.picked_up_by = vehicle_type
        container.save()
        vehicle_capacity_is_exhausted = self.schedule_repository.block_capacity_for_outbound_journey(vehicle, container)
        if vehicle_capacity_is_exhausted:
            large_scheduled_vehicle.capacity_exhausted_while_determining_onward_transportation = True
            large_scheduled_vehicle.save()
        return vehicle

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
    def _get_departure_time_of_vehicle(vehicle: Any) -> datetime.datetime:
        """get container arrival from correct source
        """
        vehicle_departure: datetime.datetime
        if isinstance(vehicle, Truck):
            truck_arrival_information: TruckArrivalInformationForDelivery = \
                vehicle.truck_arrival_information_for_delivery
            vehicle_departure = truck_arrival_information.planned_container_delivery_time_at_window_start
        else:
            vehicle_departure = vehicle.scheduled_arrival
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
        vehicle_types_and_frequencies = self.mode_of_transport_distribution[container.delivered_by].copy()

        # ignore the one vehicle type which has obviously failed, otherwise we wouldn't search for an alternative here
        previous_failed_vehicle_type: ModeOfTransport = container.picked_up_by
        del vehicle_types_and_frequencies[previous_failed_vehicle_type]

        # try to pick a better vehicle for 5 times, otherwise the previously set default values are automatically used
        for _ in range(5):
            if len(vehicle_types_and_frequencies.keys()) == 0:
                # this default value has been pre-selected anyway, nothing else to do
                return

            all_frequencies = list(vehicle_types_and_frequencies.values())
            if sum(all_frequencies) == 0:
                # this default value has been pre-selected anyway, nothing else to do
                return

            vehicle_type = random.choices(
                population=list(vehicle_types_and_frequencies.keys()),
                weights=all_frequencies
            )[0]

            if vehicle_type == ModeOfTransport.truck:
                # this default value has been pre-selected anyway, nothing else to do
                return

            if vehicle_type in ModeOfTransport.get_scheduled_vehicles():
                available_vehicles = self.schedule_repository.get_departing_vehicles(
                    start=(container_arrival + datetime.timedelta(hours=minimum_dwell_time_in_hours)),
                    end=(container_arrival + datetime.timedelta(hours=maximum_dwell_time_in_hours)),
                    vehicle_type=vehicle_type,
                    required_capacity=container.length
                )
                if len(available_vehicles) > 0:  # There is a vehicle of a new type available, so it is picked
                    self._pick_vehicle_for_container(available_vehicles, container)
                    return

                # obviously no vehicles of this type are left either, so it should also be excluded from the random
                # selection procedure in the beginning
                del vehicle_types_and_frequencies[vehicle_type]

    def _get_container_dwell_time_distribution(
            self,
            inbound_vehicle: ModeOfTransport,
            outbound_vehicle: ModeOfTransport,
            storage_requirement: StorageRequirement
    ) -> ContinuousDistribution:
        return self.container_dwell_time_distributions[inbound_vehicle][outbound_vehicle][storage_requirement]
