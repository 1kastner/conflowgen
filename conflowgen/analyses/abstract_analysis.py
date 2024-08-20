from __future__ import annotations

import abc
import datetime
import typing

# noinspection PyProtectedMember
from peewee import ModelSelect

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.vehicle import LargeScheduledVehicle
from conflowgen.tools import hashable


def get_hour_based_time_window(point_in_time: datetime.datetime) -> datetime.datetime:
    return point_in_time.replace(minute=0, second=0, microsecond=0)


def get_week_based_time_window(point_in_time: datetime.datetime) -> datetime.date:
    point_in_time = get_hour_based_time_window(point_in_time)
    monday_of_its_week = (point_in_time - datetime.timedelta(days=point_in_time.weekday())).date()
    return monday_of_its_week


def get_hour_based_range(
        start: datetime.datetime,
        end: datetime.datetime,
        include_end: bool
) -> typing.List[datetime.datetime]:
    result = [
        start + datetime.timedelta(hours=hours)
        for hours in range(0, int((end - start).total_seconds() // 3600))
    ]
    if include_end:
        result += [end]
    return result


SECONDS_IN_WEEK = 604800


def get_week_based_range(start: datetime.date, end: datetime.date) -> typing.List[datetime.date]:
    return [
        start + datetime.timedelta(weeks=weeks)
        for weeks in range(0, int((end - start).total_seconds() // SECONDS_IN_WEEK))
    ] + [end]


class AbstractAnalysis(abc.ABC):

    def __init__(
            self,
            transportation_buffer: typing.Optional[float] = None
    ):
        """

        Args:
            transportation_buffer:
                The buffer, e.g. 0.2 means that 20% more containers (in TEU) can be put on a vessel
                compared to the amount of containers it had on its inbound journey - as long as the total vehicle
                capacity would not be exceeded.
        """
        self.transportation_buffer: typing.Optional[float] = None
        self.update(
            transportation_buffer=transportation_buffer
        )

    def update(
            self,
            transportation_buffer: typing.Optional[float]
    ):
        """
        For some analyses, the transportation buffer needs to be provided.

        Args:
            transportation_buffer: The buffer, e.g. 0.2 means that 20% more containers (in TEU) can be put on a vessel
                compared to the amount of containers it had on its inbound journey - as long as the total vehicle
                capacity would not be exceeded.
        """
        if transportation_buffer is not None:
            assert transportation_buffer > -1
            self.transportation_buffer = transportation_buffer

    @staticmethod
    def _restrict_storage_requirement(selected_containers: ModelSelect, storage_requirement: typing.Any) -> ModelSelect:
        if hashable(storage_requirement) and storage_requirement in set(StorageRequirement):
            selected_containers = selected_containers.where(
                Container.storage_requirement == storage_requirement
            )
        else:  # assume it is some kind of collection (list, set, ...)
            selected_containers = selected_containers.where(
                Container.storage_requirement << storage_requirement
            )
        return selected_containers

    @staticmethod
    def _restrict_container_delivered_by_vehicle_type(
            selected_containers: ModelSelect, container_delivered_by_vehicle_type: typing.Any
    ) -> (ModelSelect, list[ModeOfTransport]):
        if hashable(container_delivered_by_vehicle_type) \
                and container_delivered_by_vehicle_type in set(ModeOfTransport):
            selected_containers = selected_containers.where(
                Container.delivered_by == container_delivered_by_vehicle_type
            )
            list_of_vehicle_types = [container_delivered_by_vehicle_type]
        else:  # assume it is some kind of collection (list, set, ...)
            selected_containers = selected_containers.where(
                Container.delivered_by << container_delivered_by_vehicle_type
            )
            list_of_vehicle_types = list(container_delivered_by_vehicle_type)
        return selected_containers, list_of_vehicle_types

    @staticmethod
    def _restrict_container_picked_up_by_vehicle_type(
            selected_containers: ModelSelect, container_picked_up_by_vehicle_type: typing.Any
    ) -> (ModelSelect, list[ModeOfTransport]):
        if container_picked_up_by_vehicle_type == "scheduled vehicles":
            container_picked_up_by_vehicle_type = ModeOfTransport.get_scheduled_vehicles()
            list_of_vehicle_types = container_picked_up_by_vehicle_type
        if hashable(container_picked_up_by_vehicle_type) \
                and container_picked_up_by_vehicle_type in set(ModeOfTransport):
            selected_containers = selected_containers.where(
                Container.picked_up_by == container_picked_up_by_vehicle_type
            )
            list_of_vehicle_types = [container_picked_up_by_vehicle_type]
        else:  # assume it is some kind of collection (list, set, ...)
            selected_containers = selected_containers.where(
                Container.picked_up_by << container_picked_up_by_vehicle_type
            )
            list_of_vehicle_types = list(container_picked_up_by_vehicle_type)
        return selected_containers, list_of_vehicle_types

    @staticmethod
    def _restrict_container_picked_up_by_initial_vehicle_type(
            selected_containers: ModelSelect, container_picked_up_by_initial_vehicle_type: typing.Any
    ) -> ModelSelect:

        if container_picked_up_by_initial_vehicle_type == "scheduled vehicles":
            container_picked_up_by_initial_vehicle_type = ModeOfTransport.get_scheduled_vehicles()

        if hashable(container_picked_up_by_initial_vehicle_type) \
                and container_picked_up_by_initial_vehicle_type in set(ModeOfTransport):
            selected_containers = selected_containers.where(
                Container.picked_up_by_initial == container_picked_up_by_initial_vehicle_type
            )
        else:  # assume it is some kind of collection (list, set, ...)
            selected_containers = selected_containers.where(
                Container.picked_up_by_initial << container_picked_up_by_initial_vehicle_type
            )
        return selected_containers

    @staticmethod
    def _restrict_vehicle_type(
            selected_vehicles: ModelSelect, vehicle_type: typing.Any
    ) -> ModelSelect:
        if hashable(vehicle_type) and vehicle_type in set(ModeOfTransport):
            if vehicle_type in ModeOfTransport.get_unscheduled_vehicles():
                raise ValueError(f"Vehicle type {vehicle_type} not supported because it adheres to no schedule.")
            selected_vehicles = selected_vehicles.where(
                LargeScheduledVehicle.schedule.vehicle_type == vehicle_type
            )
        else:  # assume it is some kind of collection (list, set, ...)
            selected_vehicles = selected_vehicles.where(
                LargeScheduledVehicle.schedule.vehicle_type << vehicle_type
            )
        return selected_vehicles
