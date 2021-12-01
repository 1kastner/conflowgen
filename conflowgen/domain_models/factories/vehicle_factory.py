"""
The VehicleFactory including its exceptions.
"""
import datetime
from typing import Union

from conflowgen.domain_models.arrival_information import \
    TruckArrivalInformationForDelivery, TruckArrivalInformationForPickup
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import DeepSeaVessel, Feeder, LargeScheduledVehicle, Train, Truck, Barge


class UnnecessaryVehicleException(Exception):
    """The vehicle with its properties cannot transport anything"""
    pass


class MissingInformationException(Exception):
    """Some information should have been provided but is missing, e.g. is `None`"""
    pass


class UnrealisticValuesException(Exception):
    """Some values are completely out of range. Please adjust if over time it changes over time."""
    pass


class VehicleFactory:
    """
    Ensures many domain constraints for object creation programmatically.
    The factory does not insert any time-related information to the vehicle.
    The type hints support the programming elsewhere in this project as peewee cannot provide us
    with that support.
    """

    @staticmethod
    def create_truck(
            delivers_container: bool,
            picks_up_container: bool,
            truck_arrival_information_for_delivery: TruckArrivalInformationForDelivery = None,
            truck_arrival_information_for_pickup: TruckArrivalInformationForPickup = None
    ) -> Truck:
        """Checks all parameters for logical consistency and only then creates the new truck."""

        if (not delivers_container) and (not picks_up_container):
            raise UnnecessaryVehicleException(
                "This truck neither delivers nor picks up a container, thus it doesn't need to be generated")
        if delivers_container and not truck_arrival_information_for_delivery:
            raise MissingInformationException("Information regarding the truck arrival for delivery is missing.")
        if picks_up_container and not truck_arrival_information_for_pickup:
            raise MissingInformationException("Information regarding the truck arrival for pickup is missing.")

        truck = Truck.create(
            delivers_container=delivers_container,
            picks_up_container=picks_up_container,
            truck_arrival_information_for_delivery=truck_arrival_information_for_delivery,
            truck_arrival_information_for_pickup=truck_arrival_information_for_pickup
        )
        truck.save()
        return truck

    @staticmethod
    def _create_large_vehicle(
            capacity_in_teu: int,
            moved_capacity: int,
            scheduled_arrival: datetime.datetime,
            schedule: Schedule,
            vehicle_name: Union[str, None]
    ) -> LargeScheduledVehicle:
        """Checks all parameters for logical consistency and only then creates the new large vehicle."""

        if capacity_in_teu < 0:
            raise UnrealisticValuesException("Feeder capacity must be positive.")

        if moved_capacity < 0:
            raise UnrealisticValuesException("Feeder must move positive amount.")

        if moved_capacity > capacity_in_teu:
            raise UnrealisticValuesException("Feeder can't move more than its capacity")

        lsv = LargeScheduledVehicle.create(
            vehicle_name=vehicle_name,
            capacity_in_teu=capacity_in_teu,
            moved_capacity=moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        return lsv

    @classmethod
    def create_feeder(
            cls,
            capacity_in_teu: int,
            moved_capacity: int,
            scheduled_arrival: datetime.datetime,
            schedule: Schedule,
            vehicle_name: Union[str, None] = None
    ) -> Feeder:
        """Checks all parameters for logical consistency and only then creates the new feeder."""

        lsv = cls._create_large_vehicle(
            vehicle_name=vehicle_name,
            capacity_in_teu=capacity_in_teu,
            moved_capacity=moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        feeder = Feeder.create(
            large_scheduled_vehicle=lsv
        )
        feeder.save()
        return feeder

    @classmethod
    def create_deep_sea_vessel(
            cls,
            capacity_in_teu: int,
            moved_capacity: int,
            scheduled_arrival: datetime.datetime,
            schedule: Schedule,
            vehicle_name: Union[str, None] = None,
    ) -> DeepSeaVessel:
        """Checks all parameters for logical consistency and only then creates the new deep sea vessel."""

        lsv = cls._create_large_vehicle(
            vehicle_name=vehicle_name,
            capacity_in_teu=capacity_in_teu,
            moved_capacity=moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        deep_sea_vessel = DeepSeaVessel.create(
            large_scheduled_vehicle=lsv
        )
        deep_sea_vessel.save()
        return deep_sea_vessel

    @classmethod
    def create_train(
            cls,
            capacity_in_teu: int,
            moved_capacity: int,
            scheduled_arrival: datetime.datetime,
            schedule: Schedule,
            vehicle_name: Union[str, None] = None,
    ) -> Train:
        """Checks all parameters for logical consistency and only then creates the new train."""

        lsv = cls._create_large_vehicle(
            vehicle_name=vehicle_name,
            capacity_in_teu=capacity_in_teu,
            moved_capacity=moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        train = Train.create(
            large_scheduled_vehicle=lsv
        )
        train.save()
        return train

    @classmethod
    def create_barge(
            cls,
            capacity_in_teu: int,
            moved_capacity: int,
            scheduled_arrival: datetime.datetime,
            schedule: Schedule,
            vehicle_name: Union[str, None] = None
    ) -> Barge:
        """Checks all parameters for logical consistency and only then creates the new train."""

        lsv = cls._create_large_vehicle(
            vehicle_name=vehicle_name,
            capacity_in_teu=capacity_in_teu,
            moved_capacity=moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        barge = Barge.create(
            large_scheduled_vehicle=lsv
        )
        barge.save()
        return barge
