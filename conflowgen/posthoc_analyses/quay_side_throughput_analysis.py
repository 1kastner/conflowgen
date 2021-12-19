from __future__ import annotations

import datetime
from typing import Dict, List

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.vehicle import LargeScheduledVehicle
from conflowgen.posthoc_analyses.abstract_posthoc_analysis import AbstractPosthocAnalysis, get_week_based_time_window, \
    get_week_based_range
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class QuaySideThroughputAnalysis(AbstractPosthocAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.QuaySideThroughputAnalysis`.
    """

    QUAY_SIDE_VEHICLES = {
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder,
        # barges are counted as hinterland here
    }

    def __init__(self, transportation_buffer: float):
        super().__init__(
            transportation_buffer=transportation_buffer
        )

    @classmethod
    def get_used_quay_side_capacity_over_time(cls) -> Dict[datetime.date, float]:
        """
        For each week, the containers crossing the quay are checked. Based on this, the required quay capacity in boxes
        can be deduced - it is simply the maximum of these values. This rather coarse time window is due to the fact
        that the discharging and loading process are not modelled. At this stage, as a simplification all containers
        arriving with a vessel are discharged at once and all containers departing with a vessel are loaded at once.
        This is smoothed by the larger time window.
        """
        containers_that_pass_quay_side: List[datetime.datetime] = []

        for container in Container.select():
            mode_of_transport_at_container_arrival: ModeOfTransport = container.delivered_by
            if mode_of_transport_at_container_arrival in cls.QUAY_SIDE_VEHICLES:
                vehicle: LargeScheduledVehicle = container.delivered_by_large_scheduled_vehicle
                time_of_container_crossing_quay_side = vehicle.scheduled_arrival
                containers_that_pass_quay_side.append(time_of_container_crossing_quay_side)

            mode_of_transport_at_container_departure: ModeOfTransport = container.picked_up_by
            if mode_of_transport_at_container_departure in cls.QUAY_SIDE_VEHICLES:
                vehicle: LargeScheduledVehicle = container.picked_up_by_large_scheduled_vehicle
                time_of_container_crossing_quay_side = vehicle.scheduled_arrival
                containers_that_pass_quay_side.append(time_of_container_crossing_quay_side)

        if len(containers_that_pass_quay_side) == 0:
            return {}

        first_arrival = min(containers_that_pass_quay_side)
        last_pickup = max(containers_that_pass_quay_side)

        first_time_window = get_week_based_time_window(first_arrival) - datetime.timedelta(weeks=1)
        last_time_window = get_week_based_time_window(last_pickup) + datetime.timedelta(weeks=1)

        used_quay_side_capacity: Dict[datetime.date, float] = {
            time_window: 0
            for time_window in get_week_based_range(first_time_window, last_time_window)
        }

        for time_of_container_crossing_quay_side in containers_that_pass_quay_side:
            time_window_of_container = get_week_based_time_window(time_of_container_crossing_quay_side)
            used_quay_side_capacity[time_window_of_container] += 1

        return used_quay_side_capacity
