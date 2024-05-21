import datetime

from peewee import AutoField, BooleanField, DateTimeField
from peewee import ForeignKeyField
from peewee import IntegerField

from .arrival_information import TruckArrivalInformationForDelivery, TruckArrivalInformationForPickup
from .base_model import BaseModel
from .data_types.container_length import CONTAINER_LENGTH_TO_OCCUPIED_TEU, ContainerLength
from .field_types.container_length import ContainerLengthField
from .field_types.mode_of_transport import ModeOfTransportField
from .field_types.storage_requirement import StorageRequirementField
from .large_vehicle_schedule import Destination
from .vehicle import LargeScheduledVehicle
from .vehicle import Truck
from .data_types.storage_requirement import StorageRequirement
from ..domain_models.data_types.mode_of_transport import ModeOfTransport


class FaultyDataException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NoPickupVehicleException(Exception):
    def __init__(self, container, vehicle_type):
        self.container = container
        self.vehicle_type = vehicle_type
        message = f"The container {self.container} is not picked up by any vehicle even though a vehicle of type " \
                  f"{self.vehicle_type} should be there."
        super().__init__(message)


class Container(BaseModel):
    """A representation of the physical container that is moved through the yard."""
    id = AutoField()
    weight: int = IntegerField(
        null=False,
        help_text="The weight of the container (approximated). This value should suit to the container weight "
                  "distribution."
    )
    length: ContainerLength = ContainerLengthField(
        null=False,
        help_text="The length of the container in feet, typically 20' or 40' are used in international trade."
    )
    storage_requirement: StorageRequirement = StorageRequirementField(
        null=False,
        help_text="Some containers must be stored separately, e.g. if they are reefers or dangerous goods containers."
    )
    delivered_by: ModeOfTransport = ModeOfTransportField(
        null=False,
        help_text="This vehicle type delivers this container to the terminal. This helps to quickly pick the correct "
                  "foreign key in the next step and is thus just additional information."
    )
    picked_up_by_initial: ModeOfTransport = ModeOfTransportField(
        null=False,
        help_text="This vehicle type is first drawn randomly for picking up the container. It might be overwritten "
                  "later because no vehicle satisfies the constraints, e.g. because all vehicles of that type arrive "
                  "too early or too late or they are already full. Large deviations between `picked_up_by_initial` "
                  "and `picked_up_by` might indicate calibration issues with the random distributions or schedules."
    )
    picked_up_by: ModeOfTransport = ModeOfTransportField(
        null=False,
        help_text="This vehicle type is later actually used for picking up the container. This helps to quickly pick "
                  "the correct foreign key in the next step and is thus just additional information."
    )
    delivered_by_large_scheduled_vehicle: LargeScheduledVehicle = ForeignKeyField(
        LargeScheduledVehicle,
        null=True,
        help_text="Points at the large scheduled vehicle it is delivered by (null if truck). "
                  "Any arrival information of the container is attached to that vehicle."
    )
    delivered_by_truck: Truck = ForeignKeyField(
        Truck,
        null=True,
        help_text="Points at the truck it is delivered by (null if large scheduled vehicle). "
                  "Any arrival information of the container is attached to that vehicle)."
    )
    picked_up_by_large_scheduled_vehicle: LargeScheduledVehicle = ForeignKeyField(
        LargeScheduledVehicle,
        null=True,
        help_text="Points at the large scheduled vehicle it is picked up by (null if truck). "
                  "Any departure information of the container is attached to that vehicle."
    )
    picked_up_by_truck: Truck = ForeignKeyField(
        Truck,
        null=True,
        help_text="Points at the truck it is picked up by (null if large scheduled vehicle). "
                  "Any departure information of the container is attached to that vehicle."
    )
    destination: Destination = ForeignKeyField(
        Destination,
        null=True,
        help_text="Points at the next destination of the container. Only applicable if picked up by a large scheduled "
                  "vehicle. This information is sometimes used for better container stacking in the yard. For vessels, "
                  "this can be regarded as a simplified stowage plan, likewise for trains and barges."
    )
    emergency_pickup: bool = BooleanField(
        default=False,
        help_text="This indicates that no regular means of transport was available so that a vehicle had to be called "
                  "explicitly to pick up the container so that the maximum dwell time is not exceeded."
    )
    cached_arrival_time: datetime.datetime = DateTimeField(
        default=None,
        null=True,
        help_text="This field is used to cache the arrival time for faster evaluation of analyses."
    )
    cached_departure_time: datetime.datetime = DateTimeField(
        default=None,
        null=True,
        help_text="This field is used to cache the departure time for faster evaluation of analyses."
    )

    @property
    def occupied_teu(self) -> float:
        return CONTAINER_LENGTH_TO_OCCUPIED_TEU[self.length]

    @property
    def flow_direction(self) -> str:
        if (self.delivered_by in [ModeOfTransport.truck, ModeOfTransport.train, ModeOfTransport.barge]
                and self.picked_up_by in [ModeOfTransport.feeder, ModeOfTransport.deep_sea_vessel]):
            return "export"
        if (self.picked_up_by in [ModeOfTransport.truck, ModeOfTransport.train, ModeOfTransport.barge]
                and self.delivered_by in [ModeOfTransport.feeder, ModeOfTransport.deep_sea_vessel]):
            return "import"
        else:
            return "transshipment"

    def get_arrival_time(self) -> datetime.datetime:

        if self.cached_arrival_time is not None:
            return self.cached_arrival_time

        container_arrival_time: datetime.datetime
        if self.delivered_by == ModeOfTransport.truck:
            # noinspection PyTypeChecker
            truck: Truck = self.delivered_by_truck
            truck_arrival_information: TruckArrivalInformationForDelivery = truck.truck_arrival_information_for_delivery
            container_arrival_time = truck_arrival_information.realized_container_delivery_time
        elif self.delivered_by in ModeOfTransport.get_scheduled_vehicles():
            # noinspection PyTypeChecker
            large_scheduled_vehicle: LargeScheduledVehicle = self.delivered_by_large_scheduled_vehicle
            container_arrival_time = large_scheduled_vehicle.scheduled_arrival
        else:
            raise FaultyDataException(f"Faulty data: {self}")

        self.cached_arrival_time = container_arrival_time
        self.save()
        return container_arrival_time

    def get_departure_time(self) -> datetime.datetime:

        if self.cached_departure_time is not None:
            return self.cached_departure_time

        container_departure_time: datetime.datetime
        if self.picked_up_by_truck is not None:
            # noinspection PyTypeChecker
            truck: Truck = self.picked_up_by_truck
            arrival_time_information: TruckArrivalInformationForPickup = \
                truck.truck_arrival_information_for_pickup
            container_departure_time = arrival_time_information.realized_container_pickup_time
        elif self.picked_up_by_large_scheduled_vehicle is not None:
            # noinspection PyTypeChecker
            vehicle: LargeScheduledVehicle = self.picked_up_by_large_scheduled_vehicle
            container_departure_time = vehicle.scheduled_arrival
        else:
            raise NoPickupVehicleException(self, self.picked_up_by)

        self.cached_departure_time = container_departure_time
        self.save()
        return container_departure_time

    def __repr__(self):
        return "<Container " \
               f"weight: {self.weight}; " \
               f"length: {self.length}; " \
               f"delivered_by_large_scheduled_vehicle: {self.delivered_by_large_scheduled_vehicle}; " \
               f"delivered_by_truck: {self.delivered_by_truck}; " \
               f"picked_up_by_large_scheduled_vehicle: {self.picked_up_by_large_scheduled_vehicle}; " \
               f"picked_up_by_truck: {self.picked_up_by_truck}" \
               ">"

    def __str__(self) -> str:
        return repr(self)
