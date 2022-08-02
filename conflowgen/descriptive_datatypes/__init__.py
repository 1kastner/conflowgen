from typing import NamedTuple, Dict

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class TransshipmentAndHinterlandSplit(NamedTuple):
    """
    This tuple keeps track of how much of the capacity is transshipment (i.e., dropped off and picked up by a vessel)
    and how much is hinterland (i.e., either dropped off or picked up by a vehicle that is not a vessel, e.g. a train
    or a truck).
    """
    transshipment_capacity: float
    hinterland_capacity: float


class HinterlandModalSplit(NamedTuple):
    """
    This tuple keeps track of how much of the capacity that is either coming from or is destined to the hinterland is
    transported and by which vehicle type.
    """
    train_capacity: float
    barge_capacity: float
    truck_capacity: float


class OutboundUsedAndMaximumCapacity(NamedTuple):
    """
    This tuple keeps track of how much each vehicle type transports on the outbound journey and what the maximum
    capacity is.
    """
    used: Dict[ModeOfTransport, float]
    maximum: Dict[ModeOfTransport, float]
