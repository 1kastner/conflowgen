from typing import Dict

from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class ModeOfTransportDistributionManager:
    """
    This manager provides the interface to set and get the distribution that controls from which vehicle containers are
    transshipped to which other type of vehicle.
    """

    def __init__(self):
        self.mode_of_transport_distribution_repository = ModeOfTransportDistributionRepository()

    def get_mode_of_transport_distributions(
            self
    ) -> Dict[ModeOfTransport, Dict[ModeOfTransport, float]]:
        """

        Returns: The distribution of mode of transports dependent on the vehicle the container is delivered by.
            If a container is delivered by a vehicle of type ``<first-key>``, the floating point number describes the
            fraction that the container is later picked up by vehicle of type ``<second-key>``.

        """
        return self.mode_of_transport_distribution_repository.get_distribution()

    def set_mode_of_transport_distributions(
            self,
            distributions: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
    ) -> None:
        """

        Args:
            distributions: If a container is delivered by a vehicle of type ``<first-key>``, the floating point number
                describes the fraction that the container is later picked up by vehicle of type ``<second-key>``.
        """
        self.mode_of_transport_distribution_repository.set_mode_of_transport_distributions(distributions)
