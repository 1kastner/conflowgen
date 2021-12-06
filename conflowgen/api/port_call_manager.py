from __future__ import annotations
import datetime
from typing import List, Tuple, Union

from conflowgen.domain_models.factories.schedule_factory import ScheduleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class PortCallManager:
    """
    This manager creates schedules for services that periodically call the container terminal, e.g. ships of any size
    and trains. This explicitly does not cover the trucks which arrive according to a probability distribution.
    """

    def __init__(self):
        self.schedule_factory = ScheduleFactory()

    def add_large_scheduled_vehicle(
            self,
            vehicle_type: ModeOfTransport,
            service_name: str,
            vehicle_arrives_at: datetime.date,
            vehicle_arrives_at_time: datetime.time,
            average_vehicle_capacity: int | float,
            average_moved_capacity: int | float,
            next_destinations: Union[List[Tuple[str, float]], None] = None,
            vehicle_arrives_every_k_days: int | None = None
    ) -> None:
        """
        Add the schedule of a ship of any size or a train. The concrete vehicle instances are automatically generated
        when :meth:`.ContainerFlowGenerationManager.generate` is invoked.

        Args:
            vehicle_type: deep_sea_vessel, feeder, barge, or train
            service_name:
            vehicle_arrives_at: A date. For k > 0, it will be shifted to match the container flow start and end dates.
            vehicle_arrives_at_time: A time at the day (00:00 to 23:59).
            average_vehicle_capacity: Number of TEU that can be transported with the vehicle at most.
            average_moved_capacity: Number of TEU which is imported.
            next_destinations: Pairs of destination and frequency of the destination being chosen.
            vehicle_arrives_every_k_days: Special case: `-1` means only once and None means default, i.e. every week.
        """
        assert vehicle_type in ModeOfTransport.get_scheduled_vehicles(), f"Vehicle of type {vehicle_type} is not " \
                                                                         f"suitable as is does not periodically arrive."
        self.schedule_factory.add_schedule(
            vehicle_type=vehicle_type,
            service_name=service_name,
            vehicle_arrives_at=vehicle_arrives_at,
            vehicle_arrives_at_time=vehicle_arrives_at_time,
            average_vehicle_capacity=average_vehicle_capacity,
            average_moved_capacity=average_moved_capacity,
            next_destinations=next_destinations,
            vehicle_arrives_every_k_days=vehicle_arrives_every_k_days
        )

    def has_schedule(
            self,
            service_name: str,
            vehicle_type: ModeOfTransport
    ) -> bool:
        """

        Args:
            service_name: The name of the service which moves to a schedule that is sought for.
            vehicle_type: The mode of transport to restrict the search to.

        Returns: Whether the requested schedule already exist in the database
        """
        assert vehicle_type in ModeOfTransport.get_scheduled_vehicles(), f"Vehicle of type {vehicle_type} not " \
                                                                         f"suitable for this method."
        return self.schedule_factory.get_schedule(service_name, vehicle_type) is not None
