"""
The super class of any kind of vehicle that delivers containers to
or picks up containers from a container terminal.
"""
from __future__ import annotations

import datetime
import uuid
from abc import abstractmethod
from typing import Type

from peewee import AutoField, BooleanField, CharField, ForeignKeyField, DateTimeField
from peewee import IntegerField

from conflowgen.domain_models.arrival_information import \
    TruckArrivalInformationForDelivery, TruckArrivalInformationForPickup
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from .base_model import BaseModel
from .data_types.mode_of_transport import ModeOfTransport


class Truck(BaseModel):
    id = AutoField()
    delivers_container = BooleanField(
        help_text="If true, this truck delivers a container that continues its journey by vessel"
    )
    picks_up_container = BooleanField(
        help_text="If true, this truck picks up a container to deliver it to the hinterland"
    )
    truck_arrival_information_for_delivery = ForeignKeyField(
        TruckArrivalInformationForDelivery,
        null=True,
        unique=True,
        help_text="If `delivers_container` is true, this field must not be null. It contains the information available "
                  "at different time steps for improved yard management."
    )
    truck_arrival_information_for_pickup = ForeignKeyField(
        TruckArrivalInformationForPickup,
        null=True,
        unique=True,
        help_text="If `picks_up_container` is true, this field must not be null. It contains the information available "
                  "at different time steps for improved yard management."
    )

    def __repr__(self):
        return f"<Truck '{self.id}'>"


class LargeScheduledVehicle(BaseModel):
    """
    This is a vehicle (either on water or on land) that moves according to a schedule,
    e.g., a weekly sequence of ports, train stations etc.

    Also check its foreign key relations such as in `large_vehicle_timetable.NextDestinations`.
    """
    id = AutoField()
    vehicle_name = CharField(
        null=False,
        default=lambda: "no-name-" + str(uuid.uuid4()),
    )
    capacity_in_teu = IntegerField(
        null=False,
        help_text="This is the vehicle capacity. It can be used, e.g., to determine how many cranes can serve it in "
                  "the subsequent model that reads in this data."
    )
    moved_capacity = IntegerField(
        null=False,
        help_text="This is the actually moved container volume in TEU for a single terminal visit on the inbound "
                  "journey."
    )
    scheduled_arrival = DateTimeField(
        null=False,
        help_text="This is the arrival time as it is noted in the schedule of the company."
    )
    realized_arrival = DateTimeField(
        null=True,
        default=None,
        help_text="If not null, this indicates the realized arrival time."
    )
    port_call_cancelled = BooleanField(
        null=False,
        default=False,
        help_text="Indicates that the port call is cancelled. Thus, no containers arrive at the terminal "
                  "and all containers meant for the vessel are redistributed to other vehicles of the same type."
    )
    schedule = ForeignKeyField(
        Schedule,
        unique=False,
        null=False,
        help_text="The schedule the vehicle adheres to."
    )
    capacity_exhausted_while_determining_onward_transportation = BooleanField(
        null=False,
        default=False,
        help_text="Indicates that during the container flow generation, the capacity of this vehicle was exhausted "
                  "while the onward transportation of containers was determined. If this applies to many vehicles, "
                  "you might want to either recheck the schedules or your ModeOfTransportDistribution as obviously "
                  "the different information does not match."
    )
    capacity_exhausted_while_allocating_space_for_export_containers = BooleanField(
        null=False,
        default=False,
        help_text="Indicates that during the container flow generation, the capacity of this vehicle was exhausted "
                  "while export containers were allocated. "
                  "If this applies to many vehicles, you might want to either recheck the schedules or your "
                  "ModeOfTransportDistribution as obviously the different information does not match."
    )

    @DataSummariesCache.cache_result
    def get_arrival_time(self) -> datetime.datetime:
        """
        Returns:
            The actual arrival time of the vehicle.
        """
        # noinspection PyTypeChecker
        return self.realized_arrival or self.scheduled_arrival

    def __repr__(self):
        return f"<LargeScheduleVehicle '{self.vehicle_name}'>"


class AbstractLargeScheduledVehicle(BaseModel):
    @property
    @abstractmethod
    def large_scheduled_vehicle(self) -> LargeScheduledVehicle:
        pass

    @staticmethod
    @abstractmethod
    def get_mode_of_transport() -> ModeOfTransport:
        pass

    @staticmethod
    def map_mode_of_transport_to_class(
            mode_of_transport: ModeOfTransport
    ) -> Type[DeepSeaVessel | Feeder | Train | Barge]:
        return {
            ModeOfTransport.deep_sea_vessel: DeepSeaVessel,
            ModeOfTransport.feeder: Feeder,
            ModeOfTransport.train: Train,
            ModeOfTransport.barge: Barge,
        }[mode_of_transport]


class Feeder(AbstractLargeScheduledVehicle):
    large_scheduled_vehicle = ForeignKeyField(
        model=LargeScheduledVehicle,
        backref="feeder",
        unique=True,
        on_delete='CASCADE',
        help_text="All general information is kept in the table `large_scheduled_vehicle`, this table only "
                  "contains vehicle type specific information"
    )

    @staticmethod
    def get_mode_of_transport() -> ModeOfTransport:
        return ModeOfTransport.feeder


class DeepSeaVessel(AbstractLargeScheduledVehicle):
    large_scheduled_vehicle = ForeignKeyField(
        model=LargeScheduledVehicle,
        backref="deep_sea_vessel",
        unique=True,
        on_delete='CASCADE',
        help_text="All general information is kept in the table `large_scheduled_vehicle`, this table only "
                  "contains vehicle type specific information"
    )

    @staticmethod
    def get_mode_of_transport() -> ModeOfTransport:
        return ModeOfTransport.deep_sea_vessel


class Train(AbstractLargeScheduledVehicle):
    large_scheduled_vehicle = ForeignKeyField(
        model=LargeScheduledVehicle,
        backref="train",
        unique=True,
        on_delete='CASCADE',
        help_text="All general information is kept in the table `large_scheduled_vehicle`, this table only "
                  "contains vehicle type specific information"
    )

    @staticmethod
    def get_mode_of_transport() -> ModeOfTransport:
        return ModeOfTransport.train


class Barge(AbstractLargeScheduledVehicle):
    large_scheduled_vehicle = ForeignKeyField(
        model=LargeScheduledVehicle,
        backref="barge",
        unique=True,
        on_delete='CASCADE',
        help_text="All general information is kept in the table `large_scheduled_vehicle`, this table only "
                  "contains vehicle type specific information"
    )

    @staticmethod
    def get_mode_of_transport() -> ModeOfTransport:
        return ModeOfTransport.barge
