from __future__ import annotations

import logging
import random
from typing import Iterable, Collection, Dict

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_repositories.container_destination_distribution_repository import \
    ContainerDestinationDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
from conflowgen.domain_models.vehicle import LargeScheduledVehicle


class AssignDestinationToContainerService:

    logger = logging.getLogger("conflowgen")

    def __init__(self):
        self.repository = ContainerDestinationDistributionRepository()
        self.distribution: Dict[Schedule, Dict[Destination, float]] | None = None
        self.reload_distribution()

    def reload_distribution(self):
        self.distribution = self.repository.get_distribution()
        self.logger.debug("Loading destination distribution...")
        for schedule, distribution_for_schedule in self.distribution.items():
            self.logger.debug(f"Load destination distribution for service '{schedule.service_name}' by "
                              f"{schedule.vehicle_type}")
            for destination, fraction in distribution_for_schedule.items():
                self.logger.debug(f"Destination '{destination.destination_name}' is frequented by {100*fraction:.2f}% "
                                  f"of the containers and is number {destination.sequence_id}")

    def assign(self):
        destination_with_distinct_schedules: Collection[Destination] = Destination.select(
            Destination.belongs_to_schedule).distinct()
        schedules = [destination.belongs_to_schedule for destination in destination_with_distinct_schedules]
        schedule: Schedule
        number_iterations = len(schedules)
        for i, schedule in enumerate(schedules):
            self.logger.debug(f"Assign destinations to containers that leave the terminal with the service "
                              f"'{schedule.service_name}' of the vehicle type {schedule.vehicle_type}, "
                              f"progress: {i+1} / {number_iterations} ({100*(i + 1)/number_iterations:.2f}%)")
            containers_moving_according_to_schedule: Iterable[Container] = Container.select().join(
                LargeScheduledVehicle, on=Container.picked_up_by_large_scheduled_vehicle
            ).where(
                Container.picked_up_by_large_scheduled_vehicle.schedule == schedule
            )
            distribution_for_schedule = self.distribution[schedule]
            destinations = list(distribution_for_schedule.keys())
            frequency_of_destinations = list(distribution_for_schedule.values())

            container: Container
            for container in containers_moving_according_to_schedule:
                sampled_destination = random.choices(
                    population=destinations,
                    weights=frequency_of_destinations
                )[0]
                container.destination = sampled_destination
                container.save()
