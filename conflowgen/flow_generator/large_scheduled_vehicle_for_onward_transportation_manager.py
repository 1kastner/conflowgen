from __future__ import annotations
import datetime
import logging
import math
import random
from typing import Tuple, List, Dict, Type, Sequence

import numpy as np
# noinspection PyProtectedMember
from peewee import fn, JOIN, ModelSelect

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
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
        number_assigned_containers = 0
        number_not_assignable_containers = 0

        self.large_scheduled_vehicle_repository.reset_cache()

        self.logger.info("Assign containers to departing vehicles that move according to a schedule...")

        # Get all containers in a random order which are picked up by a LargeScheduledVehicle
        # This way no vehicle has an advantage over another by its earlier arrival (getting better slots etc.)
        selected_containers: ModelSelect = Container.select(
        ).order_by(
            fn.Random()
        ).where(
            (Container.picked_up_by << ModeOfTransport.get_scheduled_vehicles())
            & (Container.delivered_by << ModeOfTransport.get_scheduled_vehicles())
        )

        # all the joins just exist to speed up the process and avoid triggering too many database calls
        preloaded_containers: ModelSelect = selected_containers.join(
            Truck,
            join_type=JOIN.LEFT_OUTER,
            on=(Container.delivered_by_truck == Truck.id)
        ).join(
            TruckArrivalInformationForDelivery,
            join_type=JOIN.LEFT_OUTER,
            on=(Truck.truck_arrival_information_for_delivery == TruckArrivalInformationForDelivery.id)
        ).switch(
            Container
        ).join(
            LargeScheduledVehicle,
            join_type=JOIN.LEFT_OUTER,
            on=(Container.delivered_by_large_scheduled_vehicle == LargeScheduledVehicle.id)
        )

        selected_containers_count = selected_containers.count()
        assert selected_containers_count == preloaded_containers.count(), \
            f"No container should be lost due to the join operations but " \
            f"{selected_containers_count} != {preloaded_containers.count()}"

        self.logger.info(f"In total, {len(preloaded_containers)} containers continue their journey on a vehicle that "
                         f"adhere to a schedule, assigning these containers to their respective vehicles...")
        container: Container
        for i, container in enumerate(preloaded_containers):
            i += 1
            if i % 1000 == 0 or i == 1 or i == selected_containers_count:
                self.logger.info(
                    f"Progress: {i} / {selected_containers_count} ({i / selected_containers_count:.2%}) "
                    f"containers have been assigned to a scheduled vehicle to leave the terminal again."
                )

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
                    # We are lucky and the vehicle has accepted the container for its outbound journey
                    number_assigned_containers += 1
                    continue
            # No vehicle is available, either due to operational constraints or we really ran out of vehicles.
            number_not_assignable_containers += 1
            self._find_alternative_mode_of_transportation(
                container, container_arrival, minimum_dwell_time_in_hours, maximum_dwell_time_in_hours
            )

        number_containers = number_assigned_containers + number_not_assignable_containers
        assert number_containers == selected_containers_count, \
            f"All containers should have been treated but {number_containers} != {selected_containers.count()}"
        if number_containers == 0:
            self.logger.info("No containers are moved from one vehicle adhering to a schedule to another one.")
        else:
            assigned_as_fraction = number_assigned_containers / number_containers
            self.logger.info("Containers for which no outgoing vehicle adhering to a schedule could be found: "
                             f"{assigned_as_fraction:.2%}. These will be re-assigned to another vehicle type, "
                             "such as a truck.")

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

    def _save_chosen_vehicle(self, container: Container, vehicle: Type[AbstractLargeScheduledVehicle]):

        # noinspection PyTypeChecker
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
            # There is only one vehicle available, no need to do all the calculations.
            return available_vehicles[0]

        vehicles_and_their_respective_free_capacity = {}
        for vehicle in available_vehicles:
            free_capacity = self.large_scheduled_vehicle_repository.get_free_capacity_for_outbound_journey(vehicle)
            if free_capacity >= ContainerLength.get_factor(ContainerLength.other):
                vehicles_and_their_respective_free_capacity[vehicle] = free_capacity

        if len(available_vehicles) == 0:
            # After filtering, there are no vehicles left, so nothing can be done.
            return None

        if len(available_vehicles) == 1:
            # There is only one vehicle available, no need to do all the calculations.
            return available_vehicles[0]

        # overwrite variables to drop those vehicles without free capacities - they are not really available anyway
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
        free_capacities_as_array = np.array(free_capacities)
        total_probabilities = multiply_discretized_probability_densities(
            free_capacities_as_array / free_capacities_as_array.sum(),
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

    @DataSummariesCache.cache_result
    def _get_arrival_time_of_container(self, container: Container) -> datetime.datetime:
        """get container arrival from correct source
        """
        return container.get_arrival_time()

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
                # If the vehicle is not None, that means everything has worked out, and we are done here.
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
