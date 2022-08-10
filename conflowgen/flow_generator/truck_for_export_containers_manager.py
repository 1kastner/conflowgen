from __future__ import annotations
import datetime
import random
from typing import Dict

from .abstract_truck_for_containers_manager import AbstractTruckForContainersManager
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
            container_departure_time: datetime.datetime
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

        truck_arrival_distribution_slice = truck_arrival_distribution.get_distribution_slice(
            start_as_datetime=(
                    container_departure_time
                    - datetime.timedelta(hours=maximum_dwell_time_in_hours)
            )
        )
        assert max(truck_arrival_distribution_slice) < maximum_dwell_time_in_hours, \
            f"{max(truck_arrival_distribution_slice)} < {maximum_dwell_time_in_hours} was harmed for container " \
            f"{container}."

        delivery_time_window_start = self._get_time_window_of_truck_arrival(
            container_dwell_time_distribution, truck_arrival_distribution_slice
        )

        # arrival within the last time slot
        random_time_component = random.uniform(0, self.time_window_length_in_hours - (1 / 60))
        assert 0 <= random_time_component < self.time_window_length_in_hours, \
            "The random time component must be shorter than the length of the time slot"

        # go back to the earliest possible day
        truck_arrival_time = (
                # go back to the earliest time window
                container_departure_time
                - datetime.timedelta(hours=(maximum_dwell_time_in_hours - 1))

                # add the selected time window identifier
                + datetime.timedelta(hours=delivery_time_window_start)

                # spread the truck arrivals withing the time window.
                + datetime.timedelta(hours=random_time_component)

                # With the random time component, a point probably close to one hour is added which might harm the
                # required minimum container dwell time.
                - datetime.timedelta(hours=1)
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
            teu_total += ContainerLength.get_factor(container.length)
        self.logger.info(f"All {number_containers} trucks that deliver a container are created now, moving "
                         f"{teu_total} TEU.")
