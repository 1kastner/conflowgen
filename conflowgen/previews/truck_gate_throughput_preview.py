import math
import typing
from abc import ABC
from builtins import bool
from datetime import datetime
from collections import namedtuple

from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.previews.inbound_and_outbound_vehicle_capacity_preview import \
    InboundAndOutboundVehicleCapacityPreview
from conflowgen.api.truck_arrival_distribution_manager import TruckArrivalDistributionManager
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.distribution_validators import validate_distribution_with_one_dependent_variable
from conflowgen.previews.abstract_preview import AbstractPreview


class TruckGateThroughputPreview(AbstractPreview, ABC):
    """
    This preview shows the distribution of truck traffic throughout a given week

    The preview returns a data structure that can be used for generating reports (e.g., in text or as a figure). The
    preview is intended to provide an estimate of the truck gate throughput for the given inputs. It does not
    consider all factors that may impact the actual truck gate throughput.
    """

    def __init__(self, start_date: datetime.date, end_date: datetime.date, transportation_buffer: float):
        super().__init__(start_date, end_date, transportation_buffer)
        self.inbound_and_outbound_vehicle_capacity_preview = (
            InboundAndOutboundVehicleCapacityPreview(
                self.start_date,
                self.end_date,
                self.transportation_buffer,
            )
        )

    @DataSummariesCache.cache_result
    def hypothesize_with_mode_of_transport_distribution(
            self,
            mode_of_transport_distribution: typing.Dict[ModeOfTransport, typing.Dict[ModeOfTransport, float]]
    ):
        validate_distribution_with_one_dependent_variable(
            mode_of_transport_distribution, ModeOfTransport, ModeOfTransport, values_are_frequencies=True
        )
        self.inbound_and_outbound_vehicle_capacity_preview.hypothesize_with_mode_of_transport_distribution(
            mode_of_transport_distribution)

    @DataSummariesCache.cache_result
    def _get_total_trucks(self) -> typing.Tuple[int, int]:
        # Calculate the truck capacity for export containers using the inbound container capacities
        inbound_used_and_maximum_capacity = self.inbound_and_outbound_vehicle_capacity_preview. \
            get_inbound_capacity_of_vehicles()
        outbound_used_and_maximum_capacity = self.inbound_and_outbound_vehicle_capacity_preview.\
            get_outbound_capacity_of_vehicles()

        # Get the total truck capacity in TEU
        total_inbound_truck_capacity_in_teu = inbound_used_and_maximum_capacity.teu[ModeOfTransport.truck]
        total_outbound_truck_capacity_in_teu = outbound_used_and_maximum_capacity.used.teu[ModeOfTransport.truck]

        # Calculate the TEU factor using the container length distribution
        teu_factor = ContainerLengthDistributionRepository.get_teu_factor()

        # Calculate the total number of containers transported by truck
        total_inbound_containers_transported_by_truck = \
            int(math.ceil(total_inbound_truck_capacity_in_teu / teu_factor))
        total_outbound_containers_transported_by_truck = \
            int(math.ceil(total_outbound_truck_capacity_in_teu / teu_factor))

        total_containers_transported_by_truck_datatype = \
            namedtuple('total_containers_transported_by_truck_datatype', 'inbound outbound')
        total_containers_transported_by_truck = \
            total_containers_transported_by_truck_datatype(total_inbound_containers_transported_by_truck,
                                                           total_outbound_containers_transported_by_truck)

        return total_containers_transported_by_truck

    @DataSummariesCache.cache_result
    def _get_number_of_trucks_per_week(self) -> typing.Tuple[float, float]:
        # Calculate average number of trucks per week
        num_weeks = (self.end_date - self.start_date).days / 7
        total_trucks = self._get_total_trucks()
        inbound_trucks_per_week = total_trucks.inbound / num_weeks
        outbound_trucks_per_week = total_trucks.outbound / num_weeks

        total_weekly_trucks_datatype = namedtuple('total_weekly_trucks_datatype', 'inbound outbound')
        total_weekly_trucks = total_weekly_trucks_datatype(inbound_trucks_per_week, outbound_trucks_per_week)

        return total_weekly_trucks

    @DataSummariesCache.cache_result
    def get_weekly_truck_arrivals(self, inbound: bool = True, outbound: bool = True) -> typing.Dict[int, int]:

        assert inbound or outbound, "At least one of inbound or outbound must be True"

        # Get truck arrival distribution
        truck_arrival_probability_distribution = TruckArrivalDistributionManager().\
            get_truck_arrival_distribution()

        truck_arrival_integer_distribution = {}
        weekly_trucks = self._get_number_of_trucks_per_week()
        for time, probability in truck_arrival_probability_distribution.items():
            truck_arrival_integer_distribution[time] = 0
            if inbound:
                truck_arrival_integer_distribution[time] += int(round(probability * weekly_trucks.inbound))
            if outbound:
                truck_arrival_integer_distribution[time] += int(round(probability * weekly_trucks.outbound))

        return truck_arrival_integer_distribution
