from typing import NamedTuple, Union


class TransshipmentAndHinterlandComparison(NamedTuple):
    """
    This tuple keeps track of how much of the capacity is transshipment (i.e., dropped off and picked up by a vessel)
    and how much is hinterland (i.e., either dropped off or picked up by a vehicle that is not a vessel, e.g. a train
    or a truck).
    """
    transshipment_capacity: Union[int, float]
    hinterland_capacity: Union[int, float]


class HinterlandModalSplit(NamedTuple):
    """
    This tuple keeps track of how much of the capacity that is either coming from or is destined to the hinterland is
    transported by which vehicle type.
    """
    train_capacity: Union[int, float]
    barge_capacity: Union[int, float]
    truck_capacity: Union[int, float]
