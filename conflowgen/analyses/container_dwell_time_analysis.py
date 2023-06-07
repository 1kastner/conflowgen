from __future__ import annotations

import datetime
import typing

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.container import Container
from conflowgen.analyses.abstract_analysis import AbstractAnalysis
from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache


class ContainerDwellTimeAnalysis(AbstractAnalysis):
    """
    This analysis can be run after the synthetic data has been generated.
    The analysis returns a data structure that can be used for generating reports (e.g., in text or as a figure)
    as it is the case with :class:`.ContainerDwellTimeAnalysisReport`.
    """
    @DataSummariesCache.cache_result
    def get_container_dwell_times(
            self,
            container_delivered_by_vehicle_type: typing.Union[
                str, typing.Collection[ModeOfTransport], ModeOfTransport] = "all",
            container_picked_up_by_vehicle_type: typing.Union[
                str, typing.Collection[ModeOfTransport], ModeOfTransport] = "all",
            storage_requirement: typing.Union[
                str, typing.Collection[StorageRequirement], StorageRequirement] = "all",
            start_date: typing.Optional[datetime.datetime] = None,
            end_date: typing.Optional[datetime.datetime] = None
    ) -> set[datetime.timedelta]:
        """
        The containers are filtered according to the provided criteria.
        Then, the time between the arrival of the container in the yard and the departure of the container is
        calculated.

        Args:
            container_delivered_by_vehicle_type: One of
                ``"all"``,
                a collection of :class:`ModeOfTransport` enum values (as a list, set, or similar), or
                a single :class:`ModeOfTransport` enum value.
            container_picked_up_by_vehicle_type: One of
                ``"all"``,
                a collection of :class:`ModeOfTransport` enum values (as a list, set, or similar), or
                a single :class:`ModeOfTransport` enum value.
            storage_requirement: One of
                ``"all"``,
                a collection of :class:`StorageRequirement` enum values (as a list, set, or similar), or
                a single :class:`StorageRequirement` enum value.
            start_date:
                Only include containers that arrive after the given start time.
            end_date:
                Only include containers that depart before the given end time.

        Returns:
            A set of container dwell times.
        """
        container_dwell_times: set[datetime.timedelta] = set()

        selected_containers = Container.select()

        if storage_requirement != "all":
            selected_containers = self._restrict_storage_requirement(
                selected_containers, storage_requirement
            )

        if container_delivered_by_vehicle_type != "all":
            selected_containers = self._restrict_container_delivered_by_vehicle_type(
                selected_containers, container_delivered_by_vehicle_type
            )

        if container_picked_up_by_vehicle_type != "all":
            selected_containers = self._restrict_container_picked_up_by_vehicle_type(
                selected_containers, container_picked_up_by_vehicle_type
            )

        container: Container
        for container in selected_containers:
            container_enters_yard = container.get_arrival_time()
            container_leaves_yard = container.get_departure_time()
            assert container_enters_yard < container_leaves_yard, "A container should enter the yard before leaving it"
            if start_date and container_enters_yard < start_date:
                continue
            if end_date and container_leaves_yard > end_date:
                continue
            container_dwell_time = container_leaves_yard - container_enters_yard
            container_dwell_times.add(container_dwell_time)

        return container_dwell_times
