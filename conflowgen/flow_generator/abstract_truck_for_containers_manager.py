from __future__ import annotations
import abc
import logging
import math
import random
from typing import List, Tuple, Union, Optional, Dict, Sequence

from conflowgen.tools.weekly_distribution import WeeklyDistribution
from ..domain_models.data_types.storage_requirement import StorageRequirement
from ..domain_models.container import Container
from ..domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from ..domain_models.distribution_repositories.truck_arrival_distribution_repository import \
    TruckArrivalDistributionRepository
from ..domain_models.factories.vehicle_factory import VehicleFactory
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..tools.continuous_distribution import ContinuousDistribution, multiply_discretized_probability_densities


class SumOfProbabilitiesDoesNotEqualOneException(Exception):
    pass


class UnknownDistributionPropertyException(Exception):
    pass


class AbstractTruckForContainersManager(abc.ABC):
    def __init__(self):
        self.logger = logging.getLogger("conflowgen")

        self.container_dwell_time_distribution_repository = ContainerDwellTimeDistributionRepository()
        self.container_dwell_time_distributions: \
            Dict[ModeOfTransport, Dict[ModeOfTransport, Dict[StorageRequirement, ContinuousDistribution]]] | None \
            = None

        self.truck_arrival_distribution_repository = TruckArrivalDistributionRepository()

        self.truck_arrival_distributions: \
            Dict[ModeOfTransport, Dict[StorageRequirement, WeeklyDistribution | None]] = {
                vehicle: {
                    storage_requirement: None
                    for storage_requirement in StorageRequirement
                } for vehicle in ModeOfTransport
            }

        self.vehicle_factory = VehicleFactory()
        self.time_window_length_in_hours: Optional[int] = None

    @abc.abstractmethod
    def _get_container_dwell_time_distribution(
            self,
            vehicle: ModeOfTransport,
            storage_requirement: StorageRequirement
    ) -> ContinuousDistribution:
        pass

    @property
    @abc.abstractmethod
    def is_reversed(self) -> bool:
        pass

    def reload_distributions(
            self
    ) -> None:
        # noinspection PyTypeChecker
        hour_of_the_week_fraction_pairs: List[Union[Tuple[int, float], Tuple[int, int]]] = \
            list(self.truck_arrival_distribution_repository.get_distribution().items())
        self.time_window_length_in_hours = hour_of_the_week_fraction_pairs[1][0] - hour_of_the_week_fraction_pairs[0][0]

        self.container_dwell_time_distributions = self.container_dwell_time_distribution_repository.get_distributions()
        self._update_truck_arrival_and_container_dwell_time_distributions(hour_of_the_week_fraction_pairs)

    def _update_truck_arrival_and_container_dwell_time_distributions(
            self,
            hour_of_the_week_fraction_pairs: List[Union[Tuple[int, float], Tuple[int, int]]]
    ) -> None:
        for vehicle_type in ModeOfTransport:
            for storage_requirement in StorageRequirement:
                container_dwell_time_distribution = self._get_container_dwell_time_distribution(
                    vehicle_type, storage_requirement
                )

                # Adjust the minimum and maximum to harmonize with the truck slot units. While rounding, always take a
                # conservative approach. The minimum and maximum values should not be exceeded!
                container_dwell_time_distribution.minimum = int(math.ceil(
                    container_dwell_time_distribution.minimum))
                container_dwell_time_distribution.maximum = int(math.floor(
                    container_dwell_time_distribution.maximum))

                self.logger.info(f"For vehicle type {vehicle_type} and storage requirement {storage_requirement}, "
                                 "the container dwell times need to range from "
                                 f"{container_dwell_time_distribution.minimum}h to "
                                 f"{container_dwell_time_distribution.maximum}h")
                self.truck_arrival_distributions[vehicle_type][storage_requirement] = WeeklyDistribution(
                    hour_fraction_pairs=hour_of_the_week_fraction_pairs,
                    size_of_time_window_in_hours=container_dwell_time_distribution.maximum
                )

    def _get_distributions(
            self,
            container: Container
    ) -> tuple[ContinuousDistribution, WeeklyDistribution | None]:

        container_dwell_time_distribution = self.container_dwell_time_distributions[
            container.delivered_by][container.picked_up_by][container.storage_requirement]

        truck_arrival_distributions = self._get_truck_arrival_distributions(container)
        truck_arrival_distribution = truck_arrival_distributions[container.storage_requirement]

        return container_dwell_time_distribution, truck_arrival_distribution

    @abc.abstractmethod
    def _get_truck_arrival_distributions(self, container: Container) -> Dict[StorageRequirement, WeeklyDistribution]:
        pass

    def _get_time_window_of_truck_arrival(
            self,
            container_dwell_time_distribution: ContinuousDistribution,
            truck_arrival_distribution_slice: Dict[int, float],
            _debug_check_distribution_property: Optional[str] = None
    ) -> int:
        """
        Returns:
            Number of hours after the earliest possible slot
        """
        time_windows_for_truck_arrival = list(truck_arrival_distribution_slice.keys())

        truck_arrival_probabilities = list(truck_arrival_distribution_slice.values())
        container_dwell_time_probabilities = container_dwell_time_distribution.get_probabilities(
            time_windows_for_truck_arrival, reversed_distribution=self.is_reversed
        )
        total_probabilities = multiply_discretized_probability_densities(
            truck_arrival_probabilities,
            container_dwell_time_probabilities
        )

        if sum(total_probabilities) == 0:  # bad circumstances, no slot available
            raise SumOfProbabilitiesDoesNotEqualOneException(
                f"No truck slots available! {truck_arrival_probabilities} and {total_probabilities} just do not match."
            )

        selected_time_window: int
        if _debug_check_distribution_property:
            hours_with_arrivals = self._drop_where_zero(truck_arrival_distribution_slice, total_probabilities)
            if _debug_check_distribution_property == "minimum":
                selected_time_window = min(hours_with_arrivals)
            elif _debug_check_distribution_property == "maximum":
                selected_time_window = max(hours_with_arrivals)
            elif _debug_check_distribution_property == "average":
                selected_time_window = int(round(container_dwell_time_distribution.average))
            else:
                raise UnknownDistributionPropertyException(_debug_check_distribution_property)
        else:
            selected_time_window = random.choices(
                population=time_windows_for_truck_arrival,
                weights=total_probabilities
            )[0]

        if not self.is_reversed:  # truck delivery of export container
            # The container must be picked up later than the minimum dwell time
            assert container_dwell_time_distribution.minimum <= selected_time_window, \
                f"{container_dwell_time_distribution.minimum} <= {selected_time_window}"
            # The container must be picked up before the maximum dwell time is exceeded
            assert selected_time_window <= container_dwell_time_distribution.maximum, \
                f"{selected_time_window} <= {container_dwell_time_distribution.maximum}"
        else:  # truck pick-up of import container
            # If the selected time window is zero, this means that actually the maximum dwell time was selected.
            assert 0 <= selected_time_window, f"0 <= {selected_time_window}"
            # If, e.g., a truck delivers a container to a vessel and the cut-off is 12h before vessel arrival,
            # then the latest selected time window must be before that cut-off.
            dwell_time_from_earliest_point_in_time_until_cutoff = (
                    container_dwell_time_distribution.maximum - container_dwell_time_distribution.minimum
            )
            assert selected_time_window < dwell_time_from_earliest_point_in_time_until_cutoff, \
                f"{selected_time_window} < {dwell_time_from_earliest_point_in_time_until_cutoff}"

        return selected_time_window

    @staticmethod
    def _drop_where_zero(sequence: Sequence, filter_sequence: Sequence) -> list:
        new_sequence = []
        for element, filter_element in zip(sequence, filter_sequence):
            if filter_element:
                new_sequence.append(element)
        return new_sequence
