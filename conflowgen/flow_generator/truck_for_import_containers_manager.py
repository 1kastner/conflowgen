import datetime
import random
from typing import Dict

from .abstract_truck_for_containers_manager import AbstractTruckForContainersManager
from ..domain_models.data_types.storage_requirement import StorageRequirement
from ..domain_models.arrival_information import TruckArrivalInformationForPickup
from ..domain_models.container import Container
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..domain_models.vehicle import LargeScheduledVehicle
from ..tools.continuous_distribution import ContinuousDistribution
from ..tools.weekly_distribution import WeeklyDistribution


class TruckForImportContainersManager(AbstractTruckForContainersManager):

    @property
    def is_reversed(self) -> bool:
        return False

    def _get_container_dwell_time_distribution(
            self,
            vehicle: ModeOfTransport,
            storage_requirement: StorageRequirement
    ) -> ContinuousDistribution:
        return self.container_dwell_time_distributions[vehicle][ModeOfTransport.truck][storage_requirement]

    def _get_truck_arrival_distributions(self, container: Container) -> Dict[StorageRequirement, WeeklyDistribution]:
        return self.truck_arrival_distributions[container.delivered_by]

    def _get_container_pickup_time(
            self,
            container: Container,
            container_arrival_time: datetime.datetime
    ) -> datetime.datetime:

        container_dwell_time_distribution, truck_arrival_distribution = self._get_distributions(container)
        minimum_dwell_time_in_hours = container_dwell_time_distribution.minimum
        maximum_dwell_time_in_hours = container_dwell_time_distribution.maximum

        earliest_slot = container_arrival_time.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
        truck_arrival_distribution_slice = truck_arrival_distribution.get_distribution_slice(earliest_slot)

        pickup_time_window_start = self._get_time_window_of_truck_arrival(
            container_dwell_time_distribution, truck_arrival_distribution_slice
        )

        # arrival within the last time slot
        random_time_component = random.uniform(0, self.time_window_length_in_hours - (1 / 60))
        assert 0 <= random_time_component < self.time_window_length_in_hours, \
            "The random time component must be shorter than the length of the time slot"

        truck_arrival_time = (
            earliest_slot
            + datetime.timedelta(hours=pickup_time_window_start)  # these are several days, comparable to time slot
            + datetime.timedelta(hours=random_time_component)  # a small random component for the truck arrival time
        )

        dwell_time_in_hours = (truck_arrival_time - container_arrival_time).total_seconds() / 3600

        assert dwell_time_in_hours > 0, "Dwell time must be positive"
        assert minimum_dwell_time_in_hours <= dwell_time_in_hours <= maximum_dwell_time_in_hours, \
            f"{minimum_dwell_time_in_hours} <= {dwell_time_in_hours} <= {maximum_dwell_time_in_hours} " \
            f"harmed for container {container}."

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
                                 f"generated to pick up containers at the terminal.")
            delivered_by: LargeScheduledVehicle = container.delivered_by_large_scheduled_vehicle

            # assume that the vessel arrival time changes are communicated early enough so that the trucks which pick
            # up a container never try to go to the terminal before the vessel has arrived
            container_arrival_time: datetime.datetime = \
                delivered_by.realized_arrival or delivered_by.scheduled_arrival

            truck_arrival_time = self._get_container_pickup_time(container, container_arrival_time)
            truck_arrival_information_for_pickup = TruckArrivalInformationForPickup.create(
                planned_container_pickup_time_prior_berthing=None,  # TODO: set value if required
                planned_container_pickup_time_after_initial_storage=None,  # TODO: set value if required
                realized_container_pickup_time=truck_arrival_time
            )
            truck = self.vehicle_factory.create_truck(
                delivers_container=False,
                picks_up_container=True,
                truck_arrival_information_for_delivery=None,
                truck_arrival_information_for_pickup=truck_arrival_information_for_pickup
            )
            container.picked_up_by_truck = truck
            container.save()
        self.logger.info("All trucks that pick up a container have been generated.")
