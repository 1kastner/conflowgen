import typing

from conflowgen.api import AbstractDistributionManager
from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from conflowgen.application.services.average_container_dwell_time_calculator_service import \
            AverageContainerDwellTimeCalculatorService
from conflowgen.tools.continuous_distribution import ContinuousDistribution


class ContainerDwellTimeDistributionManager(AbstractDistributionManager):
    """
    This is the interface to set and get the distribution that controls how long the container remains in the yard
    before it is loaded onto a vehicle and leaves again.
    """

    def __init__(self):
        self.container_dwell_time_distribution_repository = ContainerDwellTimeDistributionRepository()

    def get_container_dwell_time_distribution(
            self
    ) -> typing.Dict[ModeOfTransport, typing.Dict[
            ModeOfTransport, typing.Dict[StorageRequirement, ContinuousDistribution]]]:
        """

        Returns:
            The container dwell time distribution depends on the vehicle the container is delivered by, picked up by,
            and the storage requirement.
        """
        return self.container_dwell_time_distribution_repository.get_distributions()

    def set_container_dwell_time_distribution(
            self,
            distribution: typing.Dict[ModeOfTransport, typing.Dict[
                ModeOfTransport, typing.Dict[StorageRequirement, typing.Dict[str, typing.Any]]]]
    ) -> None:
        """
        The container dwell time distribution depends on the vehicle the container is delivered by, picked up by,
        and the storage requirement.

        A distribution is described by the following parameters:
            * distribution_name (:obj:`str`) - The name of the distribution.
            * average (:obj:`float`) - The expected mean
            * minimum (:obj:`float`) - The lower bound
            * maximum (:obj:`float`) - The upper bound

        Currently, the distributions 'lognormal' and 'uniform' are supported.
        """
        sanitized_distribution = self._normalize_and_validate_distribution_with_two_dependent_variables(
            distribution,
            ModeOfTransport,
            ModeOfTransport,
            StorageRequirement,
            values_are_frequencies=False
        )
        self.container_dwell_time_distribution_repository.set_distributions(
            sanitized_distribution
        )
        DataSummariesCache.reset_cache()

    def get_average_container_dwell_time(self, start_date, end_date) -> float:
        """
        Uses the inbound and outbound vehicle capacities service and the mode of transport input distribution
        to calculate the weighted average container dwell time.
        Returns:
            Weighted average of all container dwell times based on inbound and outbound vehicle capacities
        """
        return AverageContainerDwellTimeCalculatorService().get_average_container_dwell_time(
            start_date=start_date,
            end_date=end_date
        )
