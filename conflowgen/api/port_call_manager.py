from __future__ import annotations
import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.factories.schedule_factory import ScheduleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class ScheduleIsNotUniqueException(Exception):
    pass


class PortCallManager:
    """
    This manager provides the interface to create schedules for services that periodically call the container terminal,
    e.g., ships of any size and trains. This explicitly does not cover the trucks which arrive according to a
    probability distribution set at
    :class:`.TruckArrivalDistributionManager`.
    """

    def __init__(self):
        self.schedule_factory = ScheduleFactory()

    def add_vehicle(
            self,
            vehicle_type: ModeOfTransport,
            service_name: str,
            vehicle_arrives_at: datetime.date,
            vehicle_arrives_at_time: datetime.time,
            average_vehicle_capacity: int,
            average_moved_capacity: int,
            next_destinations: typing.Optional[typing.List[typing.Tuple[str, float]]] = None,
            vehicle_arrives_every_k_days: typing.Optional[int] = None
    ) -> None:
        r"""
        Add the schedule of a ship of any size or a train. The concrete vehicle instances are automatically generated
        when :meth:`.ContainerFlowGenerationManager.generate` is invoked.

        Args:
            vehicle_type: One of
                :class:`ModeOfTransport.deep_sea_vessel`,
                :class:`ModeOfTransport.feeder`,
                :class:`ModeOfTransport.barge`, or
                :class:`ModeOfTransport.train`
            service_name:
                The name of the service, i.e., the shipping line or rail freight line
            vehicle_arrives_at:
                A date the service would arrive at the terminal. This can, e.g., point at the week day for weekly
                services. In any case, this is combined with the parameter ``vehicle_arrives_every_k_days`` and only
                arrivals within the time scope between ``start_date`` and ``end_date`` are considered.
            vehicle_arrives_at_time:
                A time of the day (between 00:00 and 23:59).
            average_vehicle_capacity:
                Number of TEU that can be transported with the vehicle at most.
                The number of moved containers can never exceed this number, no matter what the value for the
                ``transportation_buffer`` is set to.
            average_moved_capacity:
                The average moved capacity describes the number of TEU which the vehicle delivers to the terminal on its
                inbound journey.
                When summing up the TEU factors of each of the loaded containers on the inbound journey, this value is
                never exceeded but closely approximated.
                For the outbound journey, the containers are assigned depending on the distribution kept in
                :class:`.ModeOfTransportDistributionManager`.
                The maximum number of containers in TEU on the outbound journey of the vehicle is bound by

                .. math::

                    min(
                        \text{average_moved_capacity} \cdot \text{transportation_buffer},\text{average_vehicle_capacity}
                    )

                If you have calibrated the aforementioned distribution accordingly, the actual number of containers on
                the outbound journey in TEU should be on average the same as on the inbound journey.
                In that case, the vehicle moves ``average_moved_capacity`` number of containers in TEU on its inbound
                journey and the same number of containers in TEU again on its outbound journey.
            next_destinations:
                Pairs of destination and frequency of the destination being chosen.
            vehicle_arrives_every_k_days:
                Defaults to weekly services (arrival every 7 days).
                Other frequencies are possible as well.
                In the special case of ``-1``, only a single arrival is scheduled for day ``vehicle_arrives_at`` as long
                as the specified date lies within ``start_date`` and ``end_date``.
                This arrival is only part of the generated container flow if that arrival lies between ``start_date``
                and ``end_date``.
        """
        assert vehicle_type in ModeOfTransport.get_scheduled_vehicles(), f"Vehicle of type {vehicle_type} is not " \
                                                                         f"suitable as is does not periodically arrive."

        if self.has_schedule(service_name=service_name, vehicle_type=vehicle_type):
            raise ScheduleIsNotUniqueException(
                f"A service {service_name} for vehicle type {vehicle_type} already exists, please use another name."
            )

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
        DataSummariesCache.reset_cache()

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
            Whether the requested schedule already exist in the database.
        """
        assert vehicle_type in ModeOfTransport.get_scheduled_vehicles(), f"Vehicle of type {vehicle_type} not " \
                                                                         f"suitable for this method."
        return self.schedule_factory.get_schedule(service_name, vehicle_type) is not None
