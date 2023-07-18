from __future__ import annotations

import datetime
import typing

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class TransshipmentAndHinterlandSplit(typing.NamedTuple):
    """
    This tuple keeps track of how much of the capacity is transshipment (i.e., dropped off and picked up by a vessel)
    and how much is hinterland (i.e., either dropped off or picked up by a vehicle that is not a vessel, e.g., a train
    or a truck).
    """
    transshipment_capacity: float
    hinterland_capacity: float


class HinterlandModalSplit(typing.NamedTuple):
    """
    This tuple keeps track of how much of the capacity that is either coming from or is destined to the hinterland is
    transported and by which vehicle type.
    """
    train_capacity: float
    barge_capacity: float
    truck_capacity: float


class OutboundUsedAndMaximumCapacity(typing.NamedTuple):
    """
    This tuple keeps track of how much each vehicle type transports on the outbound journey and what the maximum
    capacity is.
    """

    #: The container volume that is actually transported, summarized by vehicle type.
    used: ContainerVolumeByVehicleType

    #: The container volume that could be transported if all capacities had been used, summarized by vehicle type.
    maximum: ContainerVolumeByVehicleType


class ContainerVolumeByVehicleType(typing.NamedTuple):
    """
    Several KPIs at container terminals can be both expressed in boxes per hour and TEU per hour (or a different time
    range).
    """

    #: The container volume expressed in TEU
    teu: typing.Dict[ModeOfTransport, float]

    #: The container volume expressed in number of boxes
    containers: typing.Optional[typing.Dict[ModeOfTransport, float]]


class ContainerVolumeFromOriginToDestination(typing.NamedTuple):
    """
    Several KPIs at container terminals can be both expressed in boxes per hour and TEU per hour (or a different time
    range).
    """

    #: The container volume expressed in number of boxes
    containers: typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]]

    #: The container volume expressed in TEU
    teu: typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]]


class VehicleIdentifier(typing.NamedTuple):
    """
    A vehicle identifier is a composition of the vehicle type, its service name, and the actual vehicle name
    """

    #: The vehicle type, e.g., 'deep_sea_vessel' or 'truck'.
    mode_of_transport: ModeOfTransport

    #: The service name, such as the name of the container service the vessel operates in. Not set for trucks.
    service_name: typing.Optional[str]

    #: The name of the vehicle if given.
    vehicle_name: typing.Optional[str]

    #: The time of arrival of the vehicle at the terminal.
    vehicle_arrival_time: datetime.datetime


class UsedYardCapacityOverTime(typing.NamedTuple):
    """
    Represents yard capacity in TEU and number of boxes.
    """

    #: The yard capacity expressed in TEU
    teu: typing.Dict[datetime.datetime, float]

    #: The yard capacity expressed in number of boxes
    containers: typing.Dict[datetime.datetime, int]
