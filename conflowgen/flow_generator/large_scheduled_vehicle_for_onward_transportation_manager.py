from __future__ import annotations
import datetime
import logging
import random
from typing import Collection, Tuple, List

from peewee import fn

from ..domain_models.arrival_information import TruckArrivalInformationForDelivery
from ..domain_models.container import Container
from ..domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..domain_models.repositories.schedule_repository import ScheduleRepository
from ..domain_models.vehicle import AbstractLargeScheduledVehicle, LargeScheduledVehicle, Truck


class LargeScheduledVehicleForOnwardTransportationManager:

    def __init__(self):
        self.logger = logging.getLogger("conflowgen")
        self.schedule_repository = ScheduleRepository()
        self.large_scheduled_vehicle_repository = self.schedule_repository.large_scheduled_vehicle_repository
        self.mode_of_transport_distribution_repository = ModeOfTransportDistributionRepository()
        self.mode_of_transport_distribution = self.mode_of_transport_distribution_repository.get_distribution()
        self.number_assigned_containers = 0
        self.number_not_assignable_containers = 0

        self.minimum_dwell_time_of_import_containers_in_hours = None
        self.minimum_dwell_time_of_export_containers_in_hours = None
        self.minimum_dwell_time_of_transshipment_containers_in_hours = None
        self.maximum_dwell_time_of_import_containers_in_hours = None
        self.maximum_dwell_time_of_export_containers_in_hours = None
        self.maximum_dwell_time_of_transshipment_containers_in_hours = None

    def reload_properties(
            self,
            minimum_dwell_time_of_import_containers_in_hours: int,
            minimum_dwell_time_of_transshipment_containers_in_hours: int,
            minimum_dwell_time_of_export_containers_in_hours: int,
            maximum_dwell_time_of_import_containers_in_hours: int,
            maximum_dwell_time_of_transshipment_containers_in_hours: int,
            maximum_dwell_time_of_export_containers_in_hours: int,
            transportation_buffer: float
    ):
        # Minimum for import, export, and transshipment
        self.minimum_dwell_time_of_import_containers_in_hours = minimum_dwell_time_of_import_containers_in_hours
        self.minimum_dwell_time_of_export_containers_in_hours = minimum_dwell_time_of_export_containers_in_hours
        self.minimum_dwell_time_of_transshipment_containers_in_hours = \
            minimum_dwell_time_of_transshipment_containers_in_hours

        # Maximum for import, export, and transshipment
        self.maximum_dwell_time_of_import_containers_in_hours = maximum_dwell_time_of_import_containers_in_hours
        self.maximum_dwell_time_of_export_containers_in_hours = maximum_dwell_time_of_export_containers_in_hours
        self.maximum_dwell_time_of_transshipment_containers_in_hours = \
            maximum_dwell_time_of_transshipment_containers_in_hours

        assert (self.minimum_dwell_time_of_import_containers_in_hours
                < self.maximum_dwell_time_of_import_containers_in_hours)
        assert (self.minimum_dwell_time_of_export_containers_in_hours
                < self.maximum_dwell_time_of_export_containers_in_hours)
        assert (self.minimum_dwell_time_of_transshipment_containers_in_hours
                < self.maximum_dwell_time_of_transshipment_containers_in_hours)

        assert -1 < transportation_buffer
        self.schedule_repository.set_transportation_buffer(transportation_buffer)
        self.logger.debug(f"Using transportation buffer of {transportation_buffer} when choosing the departing "
                          f"vehicles that adhere a schedule.")

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

            # this value has been randomly drawn during container generation for the inbound traffic
            # we try to adhere to that value as good as possible
            initial_departing_vehicle_type = container.picked_up_by

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
        """pick vehicle with the probability of its free capacity
        """
        vehicle_distribution = {
            vehicle: self.large_scheduled_vehicle_repository.get_free_capacity_for_outbound_journey(vehicle)
            for vehicle in available_vehicles
        }
        vehicle: AbstractLargeScheduledVehicle = random.choices(
            population=list(vehicle_distribution.keys()),
            weights=list(vehicle_distribution.values())
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
        if (container.picked_up_by in (ModeOfTransport.deep_sea_vessel, ModeOfTransport.feeder)
                and container.delivered_by in (ModeOfTransport.deep_sea_vessel, ModeOfTransport.feeder)):
            minimum_dwell_time_in_hours = self.minimum_dwell_time_of_transshipment_containers_in_hours
            maximum_dwell_time_in_hours = self.maximum_dwell_time_of_transshipment_containers_in_hours
        elif (container.picked_up_by in (ModeOfTransport.train, ModeOfTransport.barge)
              and container.delivered_by in (ModeOfTransport.deep_sea_vessel, ModeOfTransport.feeder)):
            minimum_dwell_time_in_hours = self.minimum_dwell_time_of_import_containers_in_hours
            maximum_dwell_time_in_hours = self.maximum_dwell_time_of_import_containers_in_hours
        elif (container.picked_up_by in (ModeOfTransport.deep_sea_vessel, ModeOfTransport.feeder)
              and container.delivered_by in (ModeOfTransport.train, ModeOfTransport.barge, ModeOfTransport.truck)):
            minimum_dwell_time_in_hours = self.minimum_dwell_time_of_export_containers_in_hours
            maximum_dwell_time_in_hours = self.maximum_dwell_time_of_export_containers_in_hours
        else:
            raise Exception(f"ModeOfTransport "
                            f"picked_up_by: {container.picked_up_by} "
                            f"delivered_by: {container.delivered_by} "
                            f"is not considered at this point.")
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
