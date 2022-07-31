from __future__ import annotations
import abc
import logging
import math
import random
from typing import List, Tuple, Union, Optional, Dict

from conflowgen.tools.weekly_distribution import WeeklyDistribution
from ..domain_models.data_types.storage_requirement import StorageRequirement
from ..domain_models.container import Container
from ..domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from ..domain_models.distribution_repositories.truck_arrival_distribution_repository import \
    TruckArrivalDistributionRepository
from ..domain_models.factories.vehicle_factory import VehicleFactory
from ..domain_models.data_types.mode_of_transport import ModeOfTransport
from ..tools.theoretical_distribution import TheoreticalDistribution, multiply_discretized_probability_densities


class AbstractTruckForContainersManager(abc.ABC):
    def __init__(self):
        self.logger = logging.getLogger("conflowgen")

        self.container_dwell_time_distribution_repository = ContainerDwellTimeDistributionRepository()
        self.container_dwell_time_distributions: \
            Dict[ModeOfTransport, Dict[ModeOfTransport, Dict[StorageRequirement, TheoreticalDistribution]]] | None \
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
    ) -> TheoreticalDistribution:
        pass

    def reload_distributions(
            self
    ) -> None:
        # noinspection PyTypeChecker
        hour_of_the_week_fraction_pairs: List[Union[Tuple[int, float], Tuple[int, int]]] = \
            list(self.truck_arrival_distribution_repository.get_distribution().items())
        self.time_window_length_in_hours = hour_of_the_week_fraction_pairs[1][0] - hour_of_the_week_fraction_pairs[0][0]

        self.container_dwell_time_distributions = self.container_dwell_time_distribution_repository.get_distributions()
        self._update_truck_arrival_distributions(hour_of_the_week_fraction_pairs)

    def _update_truck_arrival_distributions(
            self,
            hour_of_the_week_fraction_pairs: List[Union[Tuple[int, float], Tuple[int, int]]]
    ) -> None:
        for vehicle in ModeOfTransport:
            for storage_requirement in StorageRequirement:
                container_dwell_time_distribution = self._get_container_dwell_time_distribution(
                    vehicle, storage_requirement
                )

                # only work with full hours
                container_dwell_time_distribution.minimum = int(math.ceil(container_dwell_time_distribution.minimum))
                container_dwell_time_distribution.maximum = int(math.floor(container_dwell_time_distribution.maximum))

                earliest_possible_truck_slot_in_hours_after_arrival = container_dwell_time_distribution.minimum
                last_possible_truck_slot_in_hours_after_arrival = \
                    container_dwell_time_distribution.maximum - 1  # because the latest slot is reset
                number_of_feasible_truck_slots = (
                        last_possible_truck_slot_in_hours_after_arrival
                        - earliest_possible_truck_slot_in_hours_after_arrival
                )

                self.truck_arrival_distributions[vehicle][storage_requirement] = WeeklyDistribution(
                    hour_fraction_pairs=hour_of_the_week_fraction_pairs,
                    considered_time_window_in_hours=number_of_feasible_truck_slots,
                    minimum_dwell_time_in_hours=earliest_possible_truck_slot_in_hours_after_arrival,
                    context=f"{self.__class__.__name__} : {vehicle} : {storage_requirement}"
                )

    def _get_distributions(
            self,
            container: Container
    ) -> tuple[TheoreticalDistribution, WeeklyDistribution | None]:

        container_dwell_time_distribution = self.container_dwell_time_distributions[
            container.delivered_by][container.picked_up_by][container.storage_requirement]

        truck_arrival_distributions = self._get_truck_arrival_distributions(container)
        truck_arrival_distribution = truck_arrival_distributions[container.storage_requirement]

        return container_dwell_time_distribution, truck_arrival_distribution

    @abc.abstractmethod
    def _get_truck_arrival_distributions(self, container: Container) -> Dict[StorageRequirement, WeeklyDistribution]:
        pass

    @staticmethod
    def _get_time_window_of_truck_arrival(
            container_dwell_time_distribution: TheoreticalDistribution,
            truck_arrival_distribution_slice: Dict[int, float]
    ) -> int:
        """
        Returns: hour of the week when the time window starts
        """
        time_windows_for_truck_arrival = list(truck_arrival_distribution_slice.keys())
        truck_arrival_probabilities = list(truck_arrival_distribution_slice.values())
        container_dwell_time_probabilities = container_dwell_time_distribution.get_probabilities(
            time_windows_for_truck_arrival
        )
        total_probabilities = multiply_discretized_probability_densities(
            truck_arrival_probabilities,
            container_dwell_time_probabilities
        )
        selected_time_window = random.choices(
            population=time_windows_for_truck_arrival,
            weights=total_probabilities
        )[0]
        return selected_time_window
