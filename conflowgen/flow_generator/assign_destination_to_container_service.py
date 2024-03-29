from __future__ import annotations

import logging
import typing

from peewee import fn

from conflowgen.application.repositories.random_seed_store_repository import get_initialised_random_object
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_repositories.container_destination_distribution_repository import \
    ContainerDestinationDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
from conflowgen.domain_models.vehicle import LargeScheduledVehicle


class AssignDestinationToContainerService:

    logger = logging.getLogger("conflowgen")

    def __init__(self):
        self.seeded_random = get_initialised_random_object(self.__class__.__name__)

        self.repository = ContainerDestinationDistributionRepository()
        self.distribution: typing.Dict[Schedule, typing.Dict[Destination, float]] | None = None
        self.reload_distributions()

    def reload_distributions(self):
        self.distribution = self.repository.get_distribution()
        self.logger.debug("Loading destination distribution...")
        for schedule, distribution_for_schedule in self.distribution.items():
            self.logger.debug(f"Load destination distribution for service '{schedule.service_name}' by "
                              f"{schedule.vehicle_type} with {len(distribution_for_schedule)} destinations")

    def assign(self) -> None:
        """
        Whenever a container continues its journey on a vehicle that can transport larger amounts of containers,
        grouping containers in the yard helps to avoid reshuffles. The next destination for a container is determined
        in the following. This step can only be done if the next destinations of the vehicle are determined in the
        schedule (this is an optional user input). The frequency is expressed in boxes.
        """
        destination_with_distinct_schedules: typing.Iterable[Destination] = Destination.select(
            Destination.belongs_to_schedule).distinct()
        schedules = [
            destination.belongs_to_schedule
            for destination in destination_with_distinct_schedules  # pylint: disable=not-an-iterable
        ]
        schedule: Schedule
        number_iterations = len(schedules)
        for i, schedule in enumerate(schedules):
            self.logger.debug(f"Assign destinations to containers that leave the terminal with the service "
                              f"'{schedule.service_name}' of the vehicle type {schedule.vehicle_type}, "
                              f"progress: {i+1} / {number_iterations} ({100*(i + 1)/number_iterations:.2f}%)")
            containers_moving_according_to_schedule: typing.Iterable[Container] = Container.select().join(
                LargeScheduledVehicle, on=Container.picked_up_by_large_scheduled_vehicle
            ).where(
                Container.picked_up_by_large_scheduled_vehicle.schedule == schedule
            ).order_by(
                fn.assign_random_value(Container.id)
            )
            distribution_for_schedule = self.distribution[schedule]
            destinations = list(distribution_for_schedule.keys())
            frequency_of_destinations = list(distribution_for_schedule.values())

            container: Container
            for container in containers_moving_according_to_schedule:
                sampled_destination = self.seeded_random.choices(
                    population=destinations,
                    weights=frequency_of_destinations
                )[0]
                container.destination = sampled_destination
                container.save()
