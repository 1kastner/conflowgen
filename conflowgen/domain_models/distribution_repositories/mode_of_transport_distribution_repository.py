from typing import Dict

from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_validators import validate_distribution_with_one_dependent_variable


class ModeOfTransportDistributionRepository:

    @staticmethod
    def _get_fraction(
            delivered_by: ModeOfTransport,
            picked_up_by: ModeOfTransport
    ) -> float:
        """Loads the fraction of goods that are transported between the two modes of transport.
        These do not necessarily sum up to 1."""

        entry = ModeOfTransportDistribution.get(
            (ModeOfTransportDistribution.delivered_by == delivered_by)
            & (ModeOfTransportDistribution.picked_up_by == picked_up_by)
        )
        fraction = entry.fraction
        return fraction

    @classmethod
    def get_distribution(cls) -> Dict[ModeOfTransport, Dict[ModeOfTransport, float]]:
        """Loads a distribution for which all fractions are normalized to sum up to 1 for each mode of transportation.
        """
        fractions = {
            mode_of_transport_i: {
                mode_of_transport_j: cls._get_fraction(mode_of_transport_i, mode_of_transport_j)
                for mode_of_transport_j in ModeOfTransport
            }
            for mode_of_transport_i in ModeOfTransport
        }
        distributions = {}
        for mode_of_transport_i in ModeOfTransport:
            sum_over_mode_of_transport_i = sum(fractions[mode_of_transport_i].values())
            distributions[mode_of_transport_i] = {
                mode_of_transport_j: 0 if fractions[mode_of_transport_i][mode_of_transport_j] == 0
                else fractions[mode_of_transport_i][mode_of_transport_j] / sum_over_mode_of_transport_i
                for mode_of_transport_j in ModeOfTransport
            }
        return distributions

    @staticmethod
    def set_mode_of_transport_distributions(
            distributions: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
    ) -> None:
        validate_distribution_with_one_dependent_variable(distributions, ModeOfTransport, ModeOfTransport)
        ModeOfTransportDistribution.delete().execute()
        for delivered_by, picked_up_by_distribution in distributions.items():
            for picked_up_by, fraction in picked_up_by_distribution.items():
                ModeOfTransportDistribution.create(
                    delivered_by=delivered_by,
                    picked_up_by=picked_up_by,
                    fraction=fraction
                ).save()
