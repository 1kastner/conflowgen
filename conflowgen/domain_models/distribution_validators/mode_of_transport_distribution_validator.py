import math
from typing import Dict

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class ModeOfTransportDistributionTableWithDuplicatesException(Exception):
    pass


class ModeOfTransportDeliveredWithMissing(Exception):
    pass


class ModeOfTransportPickedUpByMissing(Exception):
    pass


class ModeOfTransportProportionOutOfRangeException(Exception):
    pass


class ModeOfTransportProportionsUnequalOneException(Exception):
    pass


class ModeOfTransportDistributionValidator:

    @staticmethod
    def validate(distributions: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]):
        delivered_by_entries = distributions.keys()
        if not set(delivered_by_entries) == set(ModeOfTransport):
            missing_entries = set(ModeOfTransport) - set(delivered_by_entries)
            raise ModeOfTransportDeliveredWithMissing(missing_entries)
        for delivered_by, picked_up_by_distribution in distributions.items():
            picked_up_by_entries = picked_up_by_distribution.keys()
            if not set(picked_up_by_entries) == set(ModeOfTransport):
                missing_entries = set(ModeOfTransport) - set(picked_up_by_entries)
                raise ModeOfTransportPickedUpByMissing(
                    f"delivered by: {delivered_by}, missing entries: {missing_entries}"
                )
            for picked_up_by, fraction in picked_up_by_distribution.items():
                if not (0 <= fraction <= 1):
                    raise ModeOfTransportProportionOutOfRangeException(
                        f"delivered by: {delivered_by}, picked up by: {picked_up_by}, fraction: {fraction}"
                    )
            all_fractions_for_delivered_by = sum(picked_up_by_distribution.values())
            if not math.isclose(all_fractions_for_delivered_by, 1, abs_tol=0.1):
                raise ModeOfTransportProportionsUnequalOneException(
                    f"delivered by: {delivered_by}, sum: {all_fractions_for_delivered_by}"
                )
