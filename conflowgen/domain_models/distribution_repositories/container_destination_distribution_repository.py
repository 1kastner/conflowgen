from __future__ import annotations

import math
from typing import Dict

from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination


class ContainerDestinationFractionsUnequalOneException(Exception):
    pass


class InvalidFractionException(Exception):
    pass


class ContainerDestinationDistributionRepository:

    @staticmethod
    def _validate(
            distributions: Dict[Schedule, Dict[str, float]]
    ) -> None:
        for schedule, distribution in distributions.items():
            fractions = list(distribution.values())
            for fraction in fractions:
                if fraction is None:
                    raise InvalidFractionException("Fraction is None")
                if not (0 < fraction < 1):
                    raise InvalidFractionException(f"Fraction out of range: {fraction}")
            sum_over_all_destinations = sum(fractions)
            if not math.isclose(sum_over_all_destinations, 1):
                raise ContainerDestinationFractionsUnequalOneException(schedule)

    @staticmethod
    def _get_fraction(
            belongs_to_schedule: Schedule,
            destination_name: str
    ) -> float:
        """Loads the fraction of the destination for the given destination if one is associated with the schedule."""

        assert belongs_to_schedule is not None
        assert destination_name is not None

        destination_entry = Destination.get(
            (Destination.belongs_to_schedule == belongs_to_schedule)
            & (Destination.destination_name == destination_name)
        )
        fraction = destination_entry.fraction

        return fraction

    @classmethod
    def get_distribution(cls) -> Dict[Schedule, Dict[Destination, float]]:
        """Loads a distribution for all schedules that have destinations associated with them"""
        destination: Destination
        schedule: Schedule
        distributions = {
            schedule: {
                destination: cls._get_fraction(schedule, destination.destination_name)
                for destination in Destination.select().where(
                    Destination.belongs_to_schedule == schedule
                )
            }
            for schedule in Schedule.select()
        }

        # clean all entries for which no distribution exists
        for schedule, distribution in list(distributions.items()):
            if not distribution:
                del distributions[schedule]

        return distributions

    def set_distribution(
            self,
            distribution: Dict[Schedule, Dict[Destination, float]]
    ) -> None:
        """Sets the distribution for all schedules that have destinations associated with them"""
        self._validate(distribution)
        for schedule, destination_distribution in distribution.items():
            for destination, fraction in destination_distribution.items():
                destination.fraction = fraction
                destination.save()
