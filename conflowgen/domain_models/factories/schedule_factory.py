from __future__ import annotations
import datetime
import logging
from typing import List, Tuple, Union, Optional

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule


class ScheduleFactory:

    logger = logging.getLogger("conflowgen")

    @classmethod
    def add_schedule(
            cls,
            vehicle_type: ModeOfTransport,
            service_name: str,
            vehicle_arrives_at: datetime.date,
            vehicle_arrives_at_time: datetime.time,
            average_vehicle_capacity: int,
            average_inbound_container_volume: int,
            next_destinations: Optional[List[Tuple[str, float]]],
            vehicle_arrives_every_k_days: Optional[int] = None
    ) -> None:
        """

        Args:
            vehicle_type: A scheduled vehicle type
            service_name: A unique identifier for the service given the vehicle type
            vehicle_arrives_at: date of day
            vehicle_arrives_at_time: time of the day
            average_vehicle_capacity: in TEU
            average_inbound_container_volume: in TEU
            next_destinations: distribution
            vehicle_arrives_every_k_days: Be aware of special meaning of None and -1!
        """
        assert vehicle_type in ModeOfTransport.get_scheduled_vehicles()

        # create default schedule
        schedule = Schedule.create(
            vehicle_type=vehicle_type,
            service_name=service_name,
            vehicle_arrives_at=vehicle_arrives_at,
            vehicle_arrives_at_time=vehicle_arrives_at_time,
            average_vehicle_capacity=average_vehicle_capacity,
            average_inbound_container_volume=average_inbound_container_volume
        )
        # if it is None, use the default set in peewee, otherwise overwrite
        if vehicle_arrives_every_k_days is not None:
            schedule.vehicle_arrives_every_k_days = vehicle_arrives_every_k_days
            schedule.save()

        # set next destinations if existent
        if next_destinations:
            for i, (destination_name, fraction) in enumerate(next_destinations):
                sequence_id = i + 1  # count starting from 1
                destination = Destination.get_or_none(
                    destination_name=destination_name,
                    belongs_to_schedule=schedule
                )
                if destination:
                    cls.logger.debug(
                        f"Updating destination '{destination_name}' for schedule '{schedule.service_name}' at "
                        f"the position {sequence_id} with a frequency of {fraction:.2%}"
                    )
                    # these values might differ
                    destination.fraction = fraction
                    destination.sequence_id = sequence_id
                    destination.save()
                else:
                    cls.logger.debug(
                        f"Adding destination '{destination_name}' for schedule '{schedule.service_name}' at "
                        f"the position {sequence_id} with a frequency of {fraction:.2%}"
                    )
                    Destination.create(
                        destination_name=destination_name,
                        belongs_to_schedule=schedule,
                        sequence_id=sequence_id,
                        fraction=fraction
                    )

    @staticmethod
    def get_schedule(
            service_name: str,
            vehicle_type: ModeOfTransport
    ) -> Union[Schedule, None]:
        return Schedule.get_or_none(
            (Schedule.service_name == service_name)
            & (Schedule.vehicle_type == vehicle_type)
        )
