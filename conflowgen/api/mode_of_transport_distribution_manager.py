import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.api import AbstractDistributionManager
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class ModeOfTransportDistributionManager(AbstractDistributionManager):
    """
    This is the interface to set and get the distribution that controls from which vehicle containers are
    transshipped to which other type of vehicle.
    """

    def __init__(self):
        self.mode_of_transport_distribution_repository = ModeOfTransportDistributionRepository()

    def get_mode_of_transport_distribution(
            self
    ) -> typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]]:
        """
        Returns:
            The distribution of mode of transports dependent on the vehicle the container is delivered by.
            If a container is delivered by a vehicle of type ``<first-key>``, the floating point number describes the
            fraction that the container is later picked up by vehicle of type ``<second-key>``.
        """
        return self.mode_of_transport_distribution_repository.get_distribution()

    def set_mode_of_transport_distribution(
            self,
            distribution: typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]]
    ) -> None:
        """

        Args:
            distribution: If a container is delivered by a vehicle of type ``<first-key>``, the floating point number
                describes the fraction that the container is later picked up by vehicle of type ``<second-key>``.
        """
        sanitized_distribution = self._normalize_and_validate_distribution_with_one_dependent_variable(
            distribution,
            ModeOfTransport,
            ModeOfTransport,
            values_are_frequencies=True
        )
        self.mode_of_transport_distribution_repository.set_mode_of_transport_distributions(
            sanitized_distribution
        )
        DataSummariesCache.reset_cache()
