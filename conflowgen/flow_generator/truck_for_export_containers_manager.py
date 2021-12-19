from __future__ import annotations
import datetime
import logging
import random
from typing import List, Tuple, Union

from conflowgen.tools.weekly_distribution import WeeklyDistribution
from ..domain_models.arrival_information import TruckArrivalInformationForDelivery
from ..domain_models.container import Container
from ..domain_models.distribution_repositories.truck_arrival_distribution_repository import \
    TruckArrivalDistributionRepository
from ..domain_models.factories.vehicle_factory import VehicleFactory
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..domain_models.vehicle import LargeScheduledVehicle


class TruckForExportContainersManager:
    """
    Manages all trucks.
    """

    def __init__(self, ):
        self.logger = logging.getLogger("conflowgen")
        self.truck_arrival_distribution_repository = TruckArrivalDistributionRepository()
        self.distribution: WeeklyDistribution | None = None
        self.vehicle_factory = VehicleFactory()
        self.minimum_dwell_time_in_hours: int | float | None = None
        self.maximum_dwell_time_in_hours: int | float | None = None
        self.time_window_length_in_hours: int | float | None = None

    def reload_distribution(
            self,
            minimum_dwell_time_in_hours: int | float,
            maximum_dwell_time_in_hours: int | float
    ):
        # noinspection PyTypeChecker
        hour_of_the_week_fraction_pairs: List[Union[Tuple[int, float], Tuple[int, int]]] = \
            list(self.truck_arrival_distribution_repository.get_distribution().items())
        self.minimum_dwell_time_in_hours = minimum_dwell_time_in_hours
        self.maximum_dwell_time_in_hours = maximum_dwell_time_in_hours
        self.distribution = WeeklyDistribution(
            hour_fraction_pairs=hour_of_the_week_fraction_pairs,
            considered_time_window_in_hours=self.maximum_dwell_time_in_hours - 1,  # because the latest slot is reset
            minimum_dwell_time_in_hours=self.minimum_dwell_time_in_hours
        )
        self.time_window_length_in_hours = self.distribution.time_window_length_in_hours

    def _get_container_delivery_time(
            self,
            container_departure_time: datetime.datetime
    ) -> datetime.datetime:
        latest_slot = container_departure_time.replace(minute=0, second=0, microsecond=0) - datetime.timedelta(hours=1)
        earliest_slot = (
            latest_slot
            - datetime.timedelta(hours=self.maximum_dwell_time_in_hours - 1)  # because the latest slot is reset
        )
        distribution_slice = self.distribution.get_distribution_slice(earliest_slot)

        time_windows_for_truck_arrival = list(distribution_slice.keys())
        delivery_time_window_start = random.choices(
            population=time_windows_for_truck_arrival,
            weights=list(distribution_slice.values())
        )[0]

        # arrival within the last time slot
        random_time_component = random.uniform(0, self.time_window_length_in_hours - (1 / 60))
        assert 0 <= random_time_component < self.time_window_length_in_hours, \
            "The random time component be less than the time slot"

        # go back to the earliest possible day
        truck_arrival_time = (
            earliest_slot
            + datetime.timedelta(hours=delivery_time_window_start)
            + datetime.timedelta(hours=random_time_component)
        )
        return truck_arrival_time

    def generate_trucks_for_delivering(self) -> None:
        """Looks for all containers that are supposed to be delivered by truck and creates the corresponding truck.
        """
        containers = Container.select().where(
            Container.delivered_by == ModeOfTransport.truck
        ).execute()
        self.logger.info(f"In total {len(containers)} containers are delivered by truck, creating these trucks now...")
        for i, container in enumerate(containers):
            i += 1
            if i % 1000 == 0 and i > 0:
                self.logger.info(
                    f"Progress: {i} / {len(containers)} ({100 * i / len(containers):.2f}%) trucks generated "
                    f"for export containers")
            picked_up_with: LargeScheduledVehicle = container.picked_up_by_large_scheduled_vehicle
            container_pickup_time: datetime.datetime = \
                picked_up_with.delayed_arrival or picked_up_with.scheduled_arrival
            truck_arrival_time = self._get_container_delivery_time(container_pickup_time)
            truck_arrival_information_for_delivery = TruckArrivalInformationForDelivery.create(
                planned_container_delivery_time_at_window_start=truck_arrival_time,
                realized_container_delivery_time=truck_arrival_time
            )
            truck_arrival_information_for_delivery.save()
            truck = self.vehicle_factory.create_truck(
                delivers_container=True,
                picks_up_container=False,
                truck_arrival_information_for_delivery=truck_arrival_information_for_delivery,
                truck_arrival_information_for_pickup=None
            )
            truck.save()
            container.delivered_by_truck = truck
            container.save()
        self.logger.info("All trucks that deliver a container are created now.")
