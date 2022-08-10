from __future__ import annotations

import datetime
from typing import Dict, List, Optional

from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.vehicle import Truck
from conflowgen.analyses.abstract_analysis import AbstractAnalysis, get_hour_based_time_window, get_hour_based_range
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class TruckGateThroughputAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.TruckGateThroughputAnalysisReport`.
    """

    @classmethod
    def get_throughput_over_time(
            cls,
            inbound: bool = True,
            outbound: bool = True,
            start_date: Optional[datetime.datetime] = None,
            end_date: Optional[datetime.datetime] = None
    ) -> Dict[datetime.datetime, float]:
        """
        For each hour, the trucks entering through the truck gate are checked. Based on this, the required truck gate
        capacity in boxes can be deduced.

        Args:
            start_date: When to start recording
            end_date: When to end recording
            inbound: Whether to check for trucks which deliver a container on their inbound journey
            outbound: Whether to check for trucks which pick up a container on their outbound journey
        """
        assert (inbound or outbound), "At least one of the two must be checked for"

        if None in (start_date, end_date):
            assert start_date is None
            assert end_date is None

        containers_that_pass_truck_gate: List[datetime.datetime] = []

        selected_containers = Container.select()

        selected_containers = selected_containers.where(
            (Container.delivered_by == ModeOfTransport.truck) | (Container.picked_up_by == ModeOfTransport.truck)
        )

        for container in selected_containers:
            if inbound:
                mode_of_transport_at_container_arrival: ModeOfTransport = container.delivered_by
                if mode_of_transport_at_container_arrival == ModeOfTransport.truck:
                    truck: Truck = container.delivered_by_truck
                    arrival_time_information: TruckArrivalInformationForDelivery = \
                        truck.truck_arrival_information_for_delivery
                    time_of_entering = arrival_time_information.realized_container_delivery_time
                    if start_date is None and end_date is None:
                        containers_that_pass_truck_gate.append(time_of_entering)
                    else:
                        if start_date <= time_of_entering <= end_date:
                            containers_that_pass_truck_gate.append(time_of_entering)

            if outbound:
                mode_of_transport_at_container_departure: ModeOfTransport = container.picked_up_by
                if mode_of_transport_at_container_departure == ModeOfTransport.truck:
                    truck: Truck = container.picked_up_by_truck
                    arrival_time_information: TruckArrivalInformationForPickup = \
                        truck.truck_arrival_information_for_pickup
                    time_of_leaving = arrival_time_information.realized_container_pickup_time
                    if start_date is None and end_date is None:
                        containers_that_pass_truck_gate.append(time_of_leaving)
                    else:
                        if start_date <= time_of_leaving <= end_date:
                            containers_that_pass_truck_gate.append(time_of_leaving)

        if len(containers_that_pass_truck_gate) == 0:
            return {}

        first_arrival = min(containers_that_pass_truck_gate)
        last_pickup = max(containers_that_pass_truck_gate)
        if start_date is not None:
            first_arrival = min(start_date, first_arrival)
        if end_date is not None:
            last_pickup = max(end_date, last_pickup)

        first_time_window = get_hour_based_time_window(first_arrival) - datetime.timedelta(hours=1)
        last_time_window = get_hour_based_time_window(last_pickup) + datetime.timedelta(hours=1)

        truck_gate_throughput: Dict[datetime.datetime, float] = {
            time_window: 0
            for time_window in get_hour_based_range(first_time_window, last_time_window)
        }

        for time_of_container_crossing_quay_side in containers_that_pass_truck_gate:
            time_window_of_container = get_hour_based_time_window(time_of_container_crossing_quay_side)
            truck_gate_throughput[time_window_of_container] += 1  # counted in boxes

        return truck_gate_throughput
