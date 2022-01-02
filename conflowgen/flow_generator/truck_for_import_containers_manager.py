import datetime
import logging
import random
from typing import List, Tuple, Union

from conflowgen.tools.weekly_distribution import WeeklyDistribution
from ..domain_models.arrival_information import TruckArrivalInformationForPickup
from ..domain_models.container import Container
from ..domain_models.distribution_repositories.truck_arrival_distribution_repository import \
    TruckArrivalDistributionRepository
from ..domain_models.factories.vehicle_factory import VehicleFactory
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..domain_models.vehicle import LargeScheduledVehicle


class TruckForImportContainersManager:
    def __init__(self):
        self.logger = logging.getLogger("conflowgen")
        self.truck_arrival_distribution_repository = TruckArrivalDistributionRepository()
        self.distribution: Union[WeeklyDistribution, None] = None
        self.vehicle_factory = VehicleFactory()

    def reload_distribution(self, minimum_dwell_time_in_hours: float, maximum_dwell_time_in_hours: float):
        # noinspection PyTypeChecker
        hour_of_the_week_fraction_pairs: List[Union[Tuple[int, float], Tuple[int, int]]] = \
            list(self.truck_arrival_distribution_repository.get_distribution().items())
        self.distribution = WeeklyDistribution(
            hour_fraction_pairs=hour_of_the_week_fraction_pairs,
            considered_time_window_in_hours=maximum_dwell_time_in_hours - 1,  # because the earliest slot is reset
            minimum_dwell_time_in_hours=minimum_dwell_time_in_hours
        )

    def _get_container_pickup_time(
            self,
            container_arrival_time: datetime.datetime
    ) -> datetime.datetime:
        earliest_slot = container_arrival_time.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        distribution_slice = self.distribution.get_distribution_slice(earliest_slot)
        time_windows_for_truck_arrival = list(distribution_slice.keys())
        pickup_time_window_start = random.choices(
            population=time_windows_for_truck_arrival,
            weights=list(distribution_slice.values()))[0]
        time_window_length_in_hours = (time_windows_for_truck_arrival[1] - time_windows_for_truck_arrival[0])
        random_time_component = random.uniform(0, time_window_length_in_hours)
        truck_arrival_time = (
            earliest_slot
            + datetime.timedelta(hours=pickup_time_window_start)  # these are several days, comparable to time slot
            + datetime.timedelta(hours=random_time_component)  # a small random component for the truck arrival time
        )
        return truck_arrival_time

    def generate_trucks_for_picking_up(self):
        containers = Container.select().where(
            Container.picked_up_by == ModeOfTransport.truck
        ).execute()
        self.logger.info(f"In total {len(containers)} containers are picked up by truck, creating these trucks now...")
        for i, container in enumerate(containers):
            i += 1
            if i % 1000 == 0 and i > 0:
                self.logger.info(f"Progress: {i} / {len(containers)} ({100 * i / len(containers):.2f}%) trucks "
                                 f"generated for import containers")
            delivered_by: LargeScheduledVehicle = container.delivered_by_large_scheduled_vehicle
            container_arrival_time: datetime.datetime = \
                delivered_by.delayed_arrival or delivered_by.scheduled_arrival
            truck_arrival_time = self._get_container_pickup_time(container_arrival_time)
            truck_arrival_information_for_pickup = TruckArrivalInformationForPickup.create(
                planned_container_pickup_time_prior_berthing=None,  # TODO: set value if required
                planned_container_pickup_time_after_initial_storage=None,  # TODO: set value if required
                realized_container_pickup_time=truck_arrival_time
            )
            truck_arrival_information_for_pickup.save()
            truck = self.vehicle_factory.create_truck(
                delivers_container=False,
                picks_up_container=True,
                truck_arrival_information_for_delivery=None,
                truck_arrival_information_for_pickup=truck_arrival_information_for_pickup
            )
            truck.save()
            container.picked_up_by_truck = truck
            container.save()
        self.logger.info("All trucks that pick up a container have been generated.")
