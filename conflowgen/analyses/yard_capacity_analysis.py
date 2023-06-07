from __future__ import annotations

import datetime
import typing

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.container import Container
from conflowgen.analyses.abstract_analysis import AbstractAnalysis, get_hour_based_time_window, get_hour_based_range


class YardCapacityAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.YardCapacityAnalysisReport`.
    """

    @DataSummariesCache.cache_result
    def get_used_yard_capacity_over_time(
            self,
            storage_requirement: typing.Union[str, typing.Collection, StorageRequirement] = "all",
            smoothen_peaks: bool = True
    ) -> typing.Dict[datetime.datetime, float]:
        """
        For each hour, the containers entering and leaving the yard are checked. Based on this, the required yard
        capacity in TEU can be deduced - it is simply the maximum of these values. In addition, with the parameter
        ``storage_requirement`` the yard capacity can be filtered, e.g., to only include standard containers, empty
        containers, or any other kind of subset.

        Please be aware that this method slightly overestimates the required capacity if ``smoothen_peaks`` is set to
        false.
        When one container leaves the yard at the beginning of the respective time window and another container enters
        the yard at the end of the same time window, still the TEU equivalence of both containers is recorded as the
        required yard capacity for that time window.
        Obviously, in that case the entering container could use the slot previously used by the container which left
        earlier.
        This, however, is not true if the container enters the terminal before the other container leaves.
        This minor inaccuracy might be of little importance because no yard should be planned that tight.
        If, on the other hand, ``smoothen_peaks`` is set to true, the last time window is not recorded as occupied.
        This slightly underestimates the required capacity but leads to visually more appealing curves with fewer
        spikes.

        Args:
            storage_requirement: One of
                ``"all"``,
                a collection of :class:`StorageRequirement` enum values (as a list, set, or similar), or
                a single :class:`StorageRequirement` enum value.
            smoothen_peaks: Whether to smoothen the peaks.
        Returns:
            A series of the used yard capacity in TEU over the time.
        """
        selected_containers = Container.select()

        if storage_requirement is not None and storage_requirement != "all":
            selected_containers = self._restrict_storage_requirement(selected_containers, storage_requirement)

        container_stays: typing.List[typing.Tuple[datetime.datetime, datetime.datetime, float]] = []

        container: Container
        for container in selected_containers:
            container_stays.append(
                (
                    container.get_arrival_time(),
                    container.get_departure_time(),
                    container.occupied_teu
                )
            )

        if len(container_stays) == 0:
            return {}

        first_arrival, _, _ = min(container_stays, key=lambda x: x[0])
        _, last_pickup, _ = max(container_stays, key=lambda x: x[1])

        first_time_window = get_hour_based_time_window(first_arrival) - datetime.timedelta(hours=1)
        last_time_window = get_hour_based_time_window(last_pickup) + datetime.timedelta(hours=1)

        used_yard_capacity: typing.Dict[datetime.datetime, float] = {
            time_window: 0
            for time_window in get_hour_based_range(
                first_time_window, last_time_window, include_end=(not smoothen_peaks)
            )
        }

        for (container_enters_yard, container_leaves_yard, teu_factor_of_container) in container_stays:
            time_window_at_entering = get_hour_based_time_window(container_enters_yard)
            time_window_at_leaving = get_hour_based_time_window(container_leaves_yard)
            for time_window in get_hour_based_range(
                    time_window_at_entering, time_window_at_leaving, include_end=(not smoothen_peaks)
            ):
                used_yard_capacity[time_window] += teu_factor_of_container

        return used_yard_capacity
