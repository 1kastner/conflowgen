from __future__ import annotations

from typing import NamedTuple, Dict, Optional

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

    #: The container volume that is actually transported, summarized by vehicle type.
    used: ContainerVolumeByVehicleType

    #: The container volume that could be transported if all capacities had been used, summarized by vehicle type.
    maximum: ContainerVolumeByVehicleType


class ContainerVolumeByVehicleType(NamedTuple):
    """
    Several KPIs at container terminals can be both expressed in boxes per hour and TEU per hour (or a different time
    range).
    """

    #: The container volume expressed in TEU
    teu: Dict[ModeOfTransport, float]

    #: The container volume expressed in number of boxes
    containers: Optional[Dict[ModeOfTransport, float]]


class ContainerVolumeFromOriginToDestination(NamedTuple):
    """
    Several KPIs at container terminals can be both expressed in boxes per hour and TEU per hour (or a different time
    range).
    """

    #: The container volume expressed in number of boxes
    containers: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]

    #: The container volume expressed in TEU
    teu: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
