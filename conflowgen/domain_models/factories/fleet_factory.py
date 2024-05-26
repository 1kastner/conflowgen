import datetime
from typing import List

from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import DeepSeaVessel, Feeder, Train, Barge
from .vehicle_factory import VehicleFactory


def create_arrivals_within_time_range(
        range_starts_at: datetime.date,
        vehicle_arrives_at: datetime.date,
        range_ends_at: datetime.date,
        vehicle_arrives_every_k_days: int,
        vehicle_arrives_at_time: datetime.time
) -> List[datetime.datetime]:
    """Returns a list of dates"""

    if range_ends_at <= range_starts_at:
        raise ValueError(f"Time range ill-defined: from {range_starts_at} to {range_ends_at}")

    result = []

    if vehicle_arrives_every_k_days > 1:  # usual case
        scheduled_interval = datetime.timedelta(days=vehicle_arrives_every_k_days)
        first_arrival_at_kth_day = (vehicle_arrives_at - range_starts_at) % scheduled_interval
        first_arrival_as_day = range_starts_at + first_arrival_at_kth_day

        kth_arrival = 0

        def kth_arrival_date(xth_arrival):
            return first_arrival_as_day + xth_arrival * scheduled_interval

        while kth_arrival_date(kth_arrival) <= range_ends_at:
            kth_arrival_as_datetime = datetime.datetime.combine(
                kth_arrival_date(kth_arrival),
                vehicle_arrives_at_time
            )
            result.append(kth_arrival_as_datetime)
            kth_arrival += 1

        return result

    if vehicle_arrives_every_k_days == -1:  # special case
        vehicle_arrival_time = datetime.datetime.combine(
            vehicle_arrives_at,
            vehicle_arrives_at_time
        )
        if range_starts_at <= vehicle_arrives_at <= range_ends_at:
            return [vehicle_arrival_time]
        return []


class FleetFactory:

    def __init__(self):
        self.vehicle_factory = VehicleFactory()

    def create_feeder_fleet(
            self,
            schedule: Schedule,
            first_at: datetime.date,
            latest_at: datetime.date
    ) -> List[Feeder]:
        """Creates a collection of feeder vessels.
        This factory creates a new vessel for each port call to reduce interdependence.
        Here, randomness might kick in later.
        """

        feeders = []

        arrivals = create_arrivals_within_time_range(
            first_at,
            schedule.vehicle_arrives_at,
            latest_at,
            schedule.vehicle_arrives_every_k_days,
            schedule.vehicle_arrives_at_time
        )

        for i, arrival in enumerate(arrivals):
            inbound_container_volume = schedule.average_inbound_container_volume  # here we can add randomness later
            vehicle_name = f"{i + 1}"
            feeder = self.vehicle_factory.create_feeder(
                vehicle_name=vehicle_name,
                capacity_in_teu=schedule.average_vehicle_capacity,
                inbound_container_volume=inbound_container_volume,
                scheduled_arrival=arrival,
                schedule=schedule
            )
            feeders.append(feeder)

        return feeders

    def create_deep_sea_vessel_fleet(
            self,
            schedule: Schedule,
            first_at: datetime.date,
            latest_at: datetime.date
    ) -> List[DeepSeaVessel]:
        """Creates a collection of feeder vessels.
        This factory creates a new vessel for each port call to reduce interdependence.
        Here, randomness might kick in later.
        """

        deep_sea_vessels = []

        arrivals = create_arrivals_within_time_range(
            first_at,
            schedule.vehicle_arrives_at,
            latest_at,
            schedule.vehicle_arrives_every_k_days,
            schedule.vehicle_arrives_at_time
        )

        for i, arrival in enumerate(arrivals):
            inbound_container_volume = schedule.average_inbound_container_volume  # here we can add randomness later
            vehicle_name = f"{i + 1}"

            deep_sea_vessel = self.vehicle_factory.create_deep_sea_vessel(
                vehicle_name=vehicle_name,
                capacity_in_teu=schedule.average_vehicle_capacity,
                inbound_container_volume=inbound_container_volume,
                scheduled_arrival=arrival,
                schedule=schedule
            )
            deep_sea_vessels.append(deep_sea_vessel)

        return deep_sea_vessels

    def create_train_fleet(
            self,
            schedule: Schedule,
            first_at: datetime.date,
            latest_at: datetime.date
    ) -> List[Train]:
        """Creates a collection of trains.
        """

        trains = []

        arrivals = create_arrivals_within_time_range(
            first_at,
            schedule.vehicle_arrives_at,
            latest_at,
            schedule.vehicle_arrives_every_k_days,
            schedule.vehicle_arrives_at_time
        )

        for i, arrival in enumerate(arrivals):
            inbound_container_volume = schedule.average_inbound_container_volume  # here we can add randomness later
            vehicle_name = f"{i + 1}"

            train = self.vehicle_factory.create_train(
                vehicle_name=vehicle_name,
                capacity_in_teu=schedule.average_vehicle_capacity,
                inbound_container_volume=inbound_container_volume,
                scheduled_arrival=arrival,
                schedule=schedule
            )
            trains.append(train)

        return trains

    def create_barge_fleet(
            self,
            schedule: Schedule,
            first_at: datetime.date,
            latest_at: datetime.date
    ) -> List[Barge]:
        """Creates a collection of barges.
        """

        barges = []

        arrivals = create_arrivals_within_time_range(
            first_at,
            schedule.vehicle_arrives_at,
            latest_at,
            schedule.vehicle_arrives_every_k_days,
            schedule.vehicle_arrives_at_time
        )

        for i, arrival in enumerate(arrivals):
            inbound_container_volume = schedule.average_inbound_container_volume  # here we can add randomness later
            vehicle_name = f"{i + 1}"

            barge = self.vehicle_factory.create_barge(
                vehicle_name=vehicle_name,
                capacity_in_teu=schedule.average_vehicle_capacity,
                inbound_container_volume=inbound_container_volume,
                scheduled_arrival=arrival,
                schedule=schedule
            )
            barges.append(barge)

        return barges
