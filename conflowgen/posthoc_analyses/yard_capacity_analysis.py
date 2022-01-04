from __future__ import annotations

import datetime
from typing import Dict, Tuple, List, Collection, Union

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck
from conflowgen.posthoc_analyses.abstract_posthoc_analysis import AbstractPostHocAnalysis, get_hour_based_time_window, \
    get_hour_based_range


class YardCapacityAnalysis(AbstractPostHocAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.YardCapacityAnalysisReport`.
    """

    @staticmethod
    def get_used_yard_capacity_over_time(
            storage_requirement: Union[str, Collection, StorageRequirement] = "all"
    ) -> Dict[datetime.datetime, float]:
        """
        For each hour, the containers entering and leaving the yard are checked. Based on this, the required yard
        capacity in TEU can be deduced - it is simply the maximum of these values. In addition, with the parameter
        ``storage_requirement`` the yard capacity can be filtered, e.g. to only include standard containers, empty
        containers, or any other kind of subset.

        Please be aware that this method slightly overestimates the required capacity. If one container leaves the yard
        at the beginning of the respective time window and another container enters the yard at the end of the same time
        window, still the TEU equivalence of both containers is recorded as the required yard capacity. Obviously the
        entering container could use the same slot as the container which entered later. This minor inaccuracy might be
        of little importance because no yard should be planned that tight. The benefit is that it further allows a
        faster computation.

        Args:
            storage_requirement: One of
                ``"all"``,
                a collection of :class:`StorageRequirement` enum values (as a list, set, or similar), or
                a single :class:`StorageRequirement` enum value.

        Returns:
            A series of the used yard capacity in TEU over the time.
        """
        container_stays: List[Tuple[datetime.datetime, datetime.datetime, float]] = []

        container: Container
        if storage_requirement == "all":
            selected_containers = Container.select()
        else:
            if storage_requirement in set(StorageRequirement):
                selected_containers = Container.select().where(
                    Container.storage_requirement == storage_requirement
                )
            else:  # assume it is some kind of collection (list, set, ...)
                selected_containers = Container.select().where(
                    Container.storage_requirement << storage_requirement
                )
        for container in selected_containers:
            container_enters_yard: datetime.datetime
            container_leaves_yard: datetime.datetime
            if container.delivered_by_truck is not None:
                truck: Truck = container.delivered_by_truck
                arrival_time_information: TruckArrivalInformationForDelivery = \
                    truck.truck_arrival_information_for_delivery
                container_enters_yard = arrival_time_information.realized_container_delivery_time
            elif container.delivered_by_large_scheduled_vehicle is not None:
                vehicle: LargeScheduledVehicle = container.delivered_by_large_scheduled_vehicle
                container_enters_yard = vehicle.scheduled_arrival
            else:
                raise Exception(f"Faulty data: {container}")

            if container.picked_up_by_truck is not None:
                truck: Truck = container.picked_up_by_truck
                arrival_time_information: TruckArrivalInformationForPickup = \
                    truck.truck_arrival_information_for_pickup
                container_leaves_yard = arrival_time_information.realized_container_pickup_time
            elif container.picked_up_by_large_scheduled_vehicle is not None:
                vehicle: LargeScheduledVehicle = container.picked_up_by_large_scheduled_vehicle
                container_leaves_yard = vehicle.scheduled_arrival
            else:
                raise Exception(f"Faulty data: {container}")

            teu_factor_of_container = ContainerLength.get_factor(container.length)

            container_stays.append((container_enters_yard, container_leaves_yard, teu_factor_of_container))

        if len(container_stays) == 0:
            return {}

        first_arrival, _, _ = min(container_stays, key=lambda x: x[0])
        _, last_pickup, _ = max(container_stays, key=lambda x: x[1])

        first_time_window = get_hour_based_time_window(first_arrival) - datetime.timedelta(hours=1)
        last_time_window = get_hour_based_time_window(last_pickup) + datetime.timedelta(hours=1)

        used_yard_capacity: Dict[datetime.datetime, float] = {
            time_window: 0
            for time_window in get_hour_based_range(first_time_window, last_time_window)
        }

        for (container_enters_yard, container_leaves_yard, teu_factor_of_container) in container_stays:
            time_window_at_entering = get_hour_based_time_window(container_enters_yard)
            time_window_at_leaving = get_hour_based_time_window(container_leaves_yard)
            for time_window in get_hour_based_range(time_window_at_entering, time_window_at_leaving):
                used_yard_capacity[time_window] += teu_factor_of_container

        return used_yard_capacity
