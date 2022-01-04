from __future__ import annotations

import datetime
from typing import Dict, List

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.vehicle import LargeScheduledVehicle
from conflowgen.posthoc_analyses.abstract_posthoc_analysis import AbstractPostHocAnalysis, get_week_based_time_window, \
    get_week_based_range
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class QuaySideThroughputAnalysis(AbstractPostHocAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.QuaySideThroughputAnalysisReport`.
    """

    QUAY_SIDE_VEHICLES = {
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder,
        # barges are counted as hinterland here
    }

    @classmethod
    def get_throughput_over_time(cls, inbound: bool = True, outbound: bool = True) -> Dict[datetime.date, float]:
        """
        For each week, the containers crossing the quay are checked. Based on this, the required quay capacity in boxes
        can be deduced - it is the maximum of these values (based on all the assumptions, in reality an additional
        buffer might be reasonable to add).

        The rather coarse time window is due to the fact that the discharging and loading process are not modelled. At
        this stage, as a simplification all containers arriving with a vessel are discharged at once and all containers
        departing with a vessel are loaded at once. This is smoothed by the larger time window.

        Args:
            inbound: Whether to check for vessels which deliver a container on their inbound journey
            outbound: Whether to check for vessels which pick up a container on their outbound journey
        """

        assert (inbound or outbound), "At least one of the two must be checked for"

        containers_that_pass_quay_side: List[datetime.datetime] = []

        for container in Container.select():
            if inbound:
                mode_of_transport_at_container_arrival: ModeOfTransport = container.delivered_by
                if mode_of_transport_at_container_arrival in cls.QUAY_SIDE_VEHICLES:
                    vehicle: LargeScheduledVehicle = container.delivered_by_large_scheduled_vehicle
                    time_of_container_crossing_quay_side = vehicle.scheduled_arrival
                    containers_that_pass_quay_side.append(time_of_container_crossing_quay_side)

            if outbound:
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

        quay_side_throughput: Dict[datetime.date, float] = {
            time_window: 0
            for time_window in get_week_based_range(first_time_window, last_time_window)
        }

        for time_of_container_crossing_quay_side in containers_that_pass_quay_side:
            time_window_of_container = get_week_based_time_window(time_of_container_crossing_quay_side)
            quay_side_throughput[time_window_of_container] += 1  # counted in boxes

        return quay_side_throughput
