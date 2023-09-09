from __future__ import annotations
import datetime
from typing import Dict, Optional

from peewee import fn

from .abstract_truck_for_containers_manager import AbstractTruckForContainersManager, \
    UnknownDistributionPropertyException
from ..domain_models.data_types.container_length import ContainerLength
from ..domain_models.data_types.storage_requirement import StorageRequirement
from ..domain_models.arrival_information import TruckArrivalInformationForDelivery
from ..domain_models.container import Container
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..domain_models.vehicle import LargeScheduledVehicle
from ..tools.continuous_distribution import ContinuousDistribution
from ..tools.weekly_distribution import WeeklyDistribution


class TruckForExportContainersManager(AbstractTruckForContainersManager):
    """
    This determines when the trucks deliver the container which is later picked up from the terminal by vessel, either
    feeder or deep sea vessel.
    """

    @property
    def is_reversed(self) -> bool:
        return True

    def _get_container_dwell_time_distribution(
            self,
            vehicle: ModeOfTransport,
            storage_requirement: StorageRequirement
    ) -> ContinuousDistribution:
        distribution = self.container_dwell_time_distributions[ModeOfTransport.truck][vehicle][storage_requirement]
        return distribution

    def _get_truck_arrival_distributions(self, container: Container) -> Dict[StorageRequirement, WeeklyDistribution]:
        return self.truck_arrival_distributions[container.picked_up_by]

    def _get_container_delivery_time(
            self,
            container: Container,
            container_departure_time: datetime.datetime,
            _debug_check_distribution_property: Optional[str] = None
    ) -> datetime.datetime:
        """
        When was the container delivered to the terminal, given its departure time?

        Args:
            container: The container in question
            container_departure_time: The container's departure time (fixed by a vessel or similar)

        Returns:
            The time a truck delivered the container to the terminal (some point before the vessel departs).
        """

        container_dwell_time_distribution, truck_arrival_distribution = self._get_distributions(container)
        minimum_dwell_time_in_hours = container_dwell_time_distribution.minimum
        maximum_dwell_time_in_hours = container_dwell_time_distribution.maximum

        # Example: Given the container departs at 10:15, do not check for the hour that has already started.
        # Instead, just check for the truck arrival rate at 10:00 and earlier. This is done because the truck arrival
        # rate is provided for the whole hour. If we only had 30 minutes of that hour, we would need to scale the rate
        # accordingly. This feature could be implemented in the future.
        truck_arrival_distribution_slice = truck_arrival_distribution.get_distribution_slice(
            start_as_datetime=(
                    container_departure_time.replace(minute=0, second=0, microsecond=0)
                    - datetime.timedelta(hours=maximum_dwell_time_in_hours)
            )
        )

        delivery_time_window_start = self._get_time_window_of_truck_arrival(
            container_dwell_time_distribution,
            truck_arrival_distribution_slice,
            _debug_check_distribution_property=_debug_check_distribution_property
        )

        # arrival within the last time slot
        close_to_time_window_length = self.time_window_length_in_hours - (1 / 60)
        random_time_component: float = self.seeded_random.uniform(0, close_to_time_window_length)

        if _debug_check_distribution_property is not None:
            if _debug_check_distribution_property == "minimum":
                random_time_component = 0
            elif _debug_check_distribution_property == "maximum":
                random_time_component = close_to_time_window_length
            elif _debug_check_distribution_property == "average":
                random_time_component = 0
            else:
                raise UnknownDistributionPropertyException(f"Unknown: {_debug_check_distribution_property}")

        truck_arrival_time = (
                # go back to the earliest time window
                container_departure_time.replace(minute=0, second=0, microsecond=0)
                - datetime.timedelta(hours=maximum_dwell_time_in_hours - 1)

                # add the selected time window identifier
                + datetime.timedelta(hours=delivery_time_window_start)

                # spread the truck arrivals withing the time window.
                + datetime.timedelta(hours=random_time_component)
        )

        dwell_time_in_hours = (container_departure_time - truck_arrival_time).total_seconds() / 3600

        assert dwell_time_in_hours > 0, "Dwell time must be positive"
        assert minimum_dwell_time_in_hours <= dwell_time_in_hours <= maximum_dwell_time_in_hours, \
            f"{minimum_dwell_time_in_hours} <= {dwell_time_in_hours} <= {maximum_dwell_time_in_hours} " \
            f"harmed for container {container}."

        return truck_arrival_time

    def generate_trucks_for_delivering(self) -> None:
        """Looks for all containers that are supposed to be delivered by truck and creates the corresponding truck.
        """
        containers = Container.select().where(
            Container.delivered_by == ModeOfTransport.truck
        ).order_by(
            fn.assign_random_value(Container.id)
        )
        number_containers = containers.count()
        self.logger.info(
            f"In total {number_containers} containers are delivered by truck, creating these trucks now...")
        teu_total = 0
        for i, container in enumerate(containers):
            i += 1
            if i % 1000 == 0 or i == 1 or i == number_containers:
                self.logger.info(
                    f"Progress: {i} / {number_containers} ({i / number_containers:.2%}) trucks generated "
                    f"to deliver containers to the terminal.")
            picked_up_with: LargeScheduledVehicle = container.picked_up_by_large_scheduled_vehicle

            # assume that the vessel arrival time changes are not communicated on time so that the trucks which deliver
            # a container for that vessel drop off the container too early
            container_pickup_time: datetime.datetime = picked_up_with.scheduled_arrival

            truck_arrival_time = self._get_container_delivery_time(container, container_pickup_time)
            truck_arrival_information_for_delivery = TruckArrivalInformationForDelivery.create(
                planned_container_delivery_time_at_window_start=truck_arrival_time,
                realized_container_delivery_time=truck_arrival_time
            )
            truck = self.vehicle_factory.create_truck(
                delivers_container=True,
                picks_up_container=False,
                truck_arrival_information_for_delivery=truck_arrival_information_for_delivery,
                truck_arrival_information_for_pickup=None
            )
            container.delivered_by_truck = truck
            container.save()
            teu_total += ContainerLength.get_teu_factor(container.length)
        self.logger.info(f"All {number_containers} trucks that deliver a container are created now, moving "
                         f"{teu_total} TEU.")
