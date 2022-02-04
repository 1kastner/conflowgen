from __future__ import annotations
import datetime
from typing import List, Tuple, Optional

from conflowgen.domain_models.factories.schedule_factory import ScheduleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class PortCallManager:
    """
    This manager provides the interface to creates schedules for services that periodically call the container terminal,
    e.g. ships of any size and trains. This explicitly does not cover the trucks which arrive according to a
    probability distribution set at
    :class:`.TruckArrivalDistributionManager`.
    """

    def __init__(self):
        self.schedule_factory = ScheduleFactory()

    def add_large_scheduled_vehicle(
            self,
            vehicle_type: ModeOfTransport,
            service_name: str,
            vehicle_arrives_at: datetime.date,
            vehicle_arrives_at_time: datetime.time,
            average_vehicle_capacity: int,
            average_moved_capacity: int,
            next_destinations: Optional[List[Tuple[str, float]]] = None,
            vehicle_arrives_every_k_days: Optional[int] = None
    ) -> None:
        """
        Add the schedule of a ship of any size or a train. The concrete vehicle instances are automatically generated
        when :meth:`.ContainerFlowGenerationManager.generate` is invoked.

        Args:
            vehicle_type: One of
                :class:`ModeOfTransport.deep_sea_vessel`,
                :class:`ModeOfTransport.feeder`,
                :class:`ModeOfTransport.barge`, or
                :class:`ModeOfTransport.train`
            service_name:
                The name of the service, i.e. the shipping line or rail freight line
            vehicle_arrives_at:
                A date the service would arrive at the terminal. This can e.g. point at the week day for weekly
                services. In any case, this is combined with the parameter ``vehicle_arrives_every_k_days`` and only
                arrivals within the time scope between ``start_date`` and ``end_date`` are considered.
            vehicle_arrives_at_time:
                A time at the day (between 00:00 and 23:59).
            average_vehicle_capacity:
                Number of TEU that can be transported with the vehicle at most.
            average_moved_capacity:
                Number of TEU which is imported.
            next_destinations:
                Pairs of destination and frequency of the destination being chosen.
            vehicle_arrives_every_k_days:
                Defaults to weekly services (arrival every 7 days). Other frequencies are possible as well.
                In the special case of ``-1``, only a single arrival at the day ``vehicle_arrives_at`` is scheduled.
                This arrival is only part of the generated container flow if that arrival lies between ``start_date``
                and ``end_date``.
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

        Returns:
            Whether the requested schedule already exist in the database
        """
        assert vehicle_type in ModeOfTransport.get_scheduled_vehicles(), f"Vehicle of type {vehicle_type} not " \
                                                                         f"suitable for this method."
        return self.schedule_factory.get_schedule(service_name, vehicle_type) is not None
