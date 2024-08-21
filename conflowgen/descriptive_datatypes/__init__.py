from __future__ import annotations

import datetime
import enum
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


class ContainerVolume(typing.NamedTuple):
    """
    Several KPIs at container terminals can be both expressed in boxes and TEU.
    """
    #: The container volume expressed in TEU
    teu: float

    #: The container volume expressed in number of boxes
    containers: float


class InboundAndOutboundContainerVolume(typing.NamedTuple):
    """
    Note both the inbound and outbound container volume.
    """
    #: The container volume transported by vehicles on their inbound journey
    inbound: ContainerVolume

    #: The container volume transported by vehicles on their outbound journey
    outbound: ContainerVolume


class ContainerVolumeByVehicleType(typing.NamedTuple):
    """
    Several KPIs at container terminals can be both expressed in boxes per hour and TEU per hour (or a different time
    range).
    """

    #: The container volume expressed in TEU
    teu: typing.Dict[ModeOfTransport, float]

    #: The container volume expressed in number of boxes
    containers: typing.Optional[typing.Dict[ModeOfTransport, float]]


class OutboundUsedAndMaximumCapacity(typing.NamedTuple):
    """
    This tuple keeps track of how much each vehicle type transports on the outbound journey and what the maximum
    capacity is.
    """

    #: The container volume that is actually transported, summarized by vehicle type.
    used: ContainerVolumeByVehicleType

    #: The container volume that could be transported if all capacities had been used, summarized by vehicle type.
    maximum: ContainerVolumeByVehicleType


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

    #: The vehicle identifier as it is used in the CSV export.
    id: typing.Optional[int]

    #: The vehicle type, e.g., 'deep_sea_vessel' or 'truck'.
    mode_of_transport: ModeOfTransport

    #: The service name, such as the name of the container service the vessel operates in. Not set for trucks.
    service_name: typing.Optional[str]

    #: The name of the vehicle if given. Not set for trucks.
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


class ContainersTransportedByTruck(typing.NamedTuple):
    """
    Represents the containers moved by trucks.
    """

    #: The number of containers moved on the inbound journey
    inbound: float

    #: The number of containers moved on the outbound journey
    outbound: float


class FlowDirection(enum.Enum):
    """
    Represents the flow direction based on the terminology of
    *Handbook of Terminal Planning*, edited by Jürgen W. Böse (https://link.springer.com/book/10.1007/978-3-030-39990-0)
    """

    import_flow = "import"

    export_flow = "export"

    transshipment_flow = "transshipment"

    undefined = "undefined"

    def __str__(self) -> str:
        # noinspection PyTypeChecker
        return f"{self.value}"
