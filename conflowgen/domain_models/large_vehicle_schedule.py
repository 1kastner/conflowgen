"""
Here, timetables are defined
"""
import uuid

from peewee import CharField, DateField, ForeignKeyField, IntegerField, TimeField, FloatField, AutoField

from .base_model import BaseModel
from .field_types.mode_of_transport import ModeOfTransportField


class Schedule(BaseModel):
    id = AutoField()
    service_name = CharField(
        null=False,
        default=lambda: "no-name-" + str(uuid.uuid4()),
        help_text="The name of the service. This supports the debugging process."
    )
    vehicle_type = ModeOfTransportField(
        null=False,
        help_text="This defines the vehicle type the schedule applies to."
    )
    average_vehicle_capacity = IntegerField(
        null=False,
        help_text="All vehicles moving according to this schedule have approx. this capacity measured in TEU. "
                  "This determines the number of ship-to-shore gantry cranes that can serve the vessel "
                  "or the length of the train that must be served by portal cranes in the subsequent model."
    )
    average_inbound_container_volume = IntegerField(
        null=False,
        help_text="All vehicles moving according to this schedule move approx. this amount of TEU. "
                  "The actual amount of moved TEU might deviate if necessary to realize the provided modal split."
    )
    vehicle_arrives_at = DateField(
        null=False,
        help_text="This is a fixed arrival of the vehicle. "
                  "This is taken as the base for `vehicle_arrives_every_k_days`."
    )
    vehicle_arrives_every_k_days = IntegerField(
        null=False, default=7,
        help_text="After the first arrival, the vehicle is supposed to arrive every k days."
                  "If this is -1, it means that the vehicle only arrives once."
    )
    vehicle_arrives_at_time = TimeField(
        null=True, default=None,
        help_text="If defined, this indicates the scheduled arrival time. At some container terminals, "
                  "the berths are blocked several weeks before the vessel arrives."
    )

    def __str__(self) -> str:
        return f"<Schedule: '{self.service_name}' by {self.vehicle_type}>"

    class Meta:
        indexes = (
            (('service_name', 'vehicle_type'), True),  # ensure uniqueness
        )


class Destination(BaseModel):
    belongs_to_schedule = ForeignKeyField(
        Schedule,
        null=False,
        on_delete="CASCADE",
        help_text="Indicates the schedule this destination belongs to."
    )
    sequence_id = IntegerField(
        null=False,
        help_text="The sequence the different destinations of the same schedule are approached. This can be used for a "
                  "simplified stowage representation of a vessel."
    )
    destination_name = CharField(
        null=True,
        default=lambda: "no-name-" + str(uuid.uuid4()),
        help_text="A human-readable name of the destination. While a distinguishable ID is also sufficient, human-"
                  "readable destination names make it easier to make sense of the generated data."
    )
    fraction = FloatField(
        null=True,
        help_text="The frequency of the given destination. All fractions for the destinations of the same schedule "
                  "need to add up to 1. The fractions can be set later, thus it can be null at creation."
    )

    def __str__(self) -> str:
        return f"<Destination '{self.destination_name}'>"

    class Meta:
        indexes = (
            (('belongs_to_schedule', 'sequence_id'), True),  # ensure uniqueness
        )

    @classmethod
    def initialize_index(cls):
        cls.index(
            cls.belongs_to_schedule,
            cls.destination_name,
            unique=True
        )
