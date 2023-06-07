import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.api import AbstractDistributionManager
from conflowgen.domain_models.distribution_repositories.truck_arrival_distribution_repository import \
    TruckArrivalDistributionRepository


class TruckArrivalDistributionManager(AbstractDistributionManager):
    """
    This manager provides the interface to set and get the weekly arrival rates of trucks. When the truck arrival time
    is drawn from this distribution, first a slice for the minimum and maximum dwell time is created and the arrival
    time of the truck is drawn from that period.
    All other vehicles are created based on the schedule they adhere to with the help of the
    :class:`.PortCallManager`
    """

    def __init__(self):
        self.truck_arrival_distribution_repository = TruckArrivalDistributionRepository()

    def get_truck_arrival_distribution(self) -> typing.Dict[int, float]:
        """
        Each key represents the hour in the week and each value represents the
        probability of a truck to arrive between that hour and the start of the next time slot (the successor
        is the nearest key larger than the current key).

        Returns:
            The truck arrival distribution.
        """
        return self.truck_arrival_distribution_repository.get_distribution()

    def set_truck_arrival_distribution(self, distribution: typing.Dict[int, float]) -> None:
        """

        Args:
            distribution: The truck arrival distribution.
                Each key represents the hour in the week and each value represents the
                probability of a truck to arrive between that hour and the start of the next time slot (the successor is
                the nearest key larger than the current key).
        """
        sanitized_distribution = self._normalize_and_validate_distribution_without_dependent_variables(
            distribution,
            int,
            values_are_frequencies=True
        )
        self.truck_arrival_distribution_repository.set_distribution(sanitized_distribution)
        DataSummariesCache.reset_cache()
