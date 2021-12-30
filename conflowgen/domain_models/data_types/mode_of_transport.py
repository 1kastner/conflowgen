from __future__ import annotations
import enum
from typing import List
import enum_tools.documentation


@enum_tools.documentation.document_enum
class ModeOfTransport(enum.Enum):
    """
    The mode of transport describes the vehicle type of the vehicle which either drops off or picks up a container.
    """

    # pylint: disable=line-too-long

    truck = "truck"  # doc: An external truck is sent by a freight forwarder

    train = "train"  # doc: A freight train is sent by a train operating company

    feeder = "feeder"  # doc: A feeder vessel is a rather small vessel sent by a ship operator and moves in the region

    deep_sea_vessel = "deep_sea_vessel"
    """A deep sea vessel is a rather large vessel sent by a ship operator and moves between distant regions, e.g.
    continents."""

    barge = "barge"  # doc: A barge is sent by an inland shipping operator

    @classmethod
    def get_scheduled_vehicles(cls) -> List[ModeOfTransport]:
        """
        Returns: A list of vehicles that follow a schedule
        """
        return [
            cls.train,
            cls.feeder,
            cls.deep_sea_vessel,
            cls.barge
        ]

    @classmethod
    def get_unscheduled_vehicles(cls) -> List[ModeOfTransport]:
        """
        Returns: A list of vehicles that are created as they are needed to transport a container
        """
        return [
            cls.truck
        ]

    def __str__(self):
        """
        The representation is e.g. 'feeder' instead of '<ModeOfTransport.feeder>' and thus nicer for the logs.
        """
        return self.value
