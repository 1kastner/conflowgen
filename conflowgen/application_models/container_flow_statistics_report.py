import logging
import statistics
from typing import List

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.repositories.large_scheduled_vehicle_repository import LargeScheduledVehicleRepository
from conflowgen.domain_models.vehicle import AbstractLargeScheduledVehicle, LargeScheduledVehicle


class ContainerFlowStatisticsReport:
    def __init__(self, transportation_buffer=None):
        self.large_scheduled_vehicle_repository = LargeScheduledVehicleRepository()
        self.logger = logging.getLogger("conflowgen")
        self.free_capacity_inbound_statistics = {}
        self.free_capacity_outbound_statistics = {}
        if transportation_buffer:
            self.set_transportation_buffer(transportation_buffer=transportation_buffer)

    def set_transportation_buffer(self, transportation_buffer: float):
        self.large_scheduled_vehicle_repository.set_transportation_buffer(transportation_buffer)
        self.logger.info(f"Use transportation buffer of {transportation_buffer} for reporting statistics.")

    def generate(self):
        vehicles_of_types = self.large_scheduled_vehicle_repository.load_all_vehicles()
        self._generate_free_capacity_statistics(vehicles_of_types)

    def _generate_free_capacity_statistics(self, vehicles_of_types):
        buffer_factor = 1 + self.large_scheduled_vehicle_repository.transportation_buffer
        free_capacities_inbound = {}
        free_capacities_outbound = {}
        vehicle_types: ModeOfTransport
        vehicles: List[AbstractLargeScheduledVehicle]
        for vehicle_type, vehicles in vehicles_of_types.items():
            for vehicle in vehicles:
                large_scheduled_vehicle: LargeScheduledVehicle = vehicle.large_scheduled_vehicle
                free_capacity_inbound = self.large_scheduled_vehicle_repository.get_free_capacity_for_inbound_journey(
                    vehicle
                )
                free_capacity_outbound = self.large_scheduled_vehicle_repository.get_free_capacity_for_outbound_journey(
                    vehicle
                )
                assert free_capacity_inbound <= large_scheduled_vehicle.capacity_in_teu, \
                    f"A vehicle can only load at maximum its capacity, but for vehicle {vehicle} the free capacity " \
                    f"of {free_capacity_inbound} for inbound does not match with the capacity of the vehicle of " \
                    f"{large_scheduled_vehicle.capacity_in_teu} TEU"
                assert free_capacity_outbound <= large_scheduled_vehicle.capacity_in_teu, \
                    f"A vehicle can only load at maximum its capacity, but for vehicle {vehicle} the free capacity " \
                    f"of {free_capacity_outbound} for outbound does not match with the capacity of the vehicle of " \
                    f"{large_scheduled_vehicle.capacity_in_teu} TEU"

                assert (free_capacity_inbound <= large_scheduled_vehicle.moved_capacity), \
                    f"A vehicle must not exceed its moved capacity, but for vehicle {vehicle} the free " \
                    f"capacity of {free_capacity_inbound} TEU for inbound does not match with the moved capacity " \
                    f"of {large_scheduled_vehicle.moved_capacity}"
                moved_capacity_with_outbound_buffer = (large_scheduled_vehicle.moved_capacity * buffer_factor)
                assert (free_capacity_outbound <= moved_capacity_with_outbound_buffer), \
                    f"A vehicle must not exceed its transportation buffer, but for vehicle {vehicle} the free " \
                    f"capacity of {free_capacity_outbound} for outbound does not match with the moved capacity " \
                    f"(including the outbound buffer) of {moved_capacity_with_outbound_buffer}"

                free_capacities_inbound[vehicle] = free_capacity_inbound
                free_capacities_outbound[vehicle] = free_capacity_outbound
        self.free_capacity_inbound_statistics = self.descriptive_statistics(free_capacities_inbound.values())
        self.free_capacity_outbound_statistics = self.descriptive_statistics(free_capacities_outbound.values())

    @staticmethod
    def descriptive_statistics(list_of_values):
        mean = statistics.mean(list_of_values)
        minimum = min(list_of_values)
        maximum = max(list_of_values)
        stddev = statistics.stdev(list_of_values) if len(list_of_values) > 1 else 0
        return {
            "mean": mean,
            "minimum": minimum,
            "maximum": maximum,
            "stddev": stddev
        }

    def get_text_representation(self):
        report = f"""
Free Inbound Capacity Statistics
Minimum: {self.free_capacity_inbound_statistics["minimum"]:.2f}
Maximum: {self.free_capacity_inbound_statistics["maximum"]:.2f}
Mean:    {self.free_capacity_inbound_statistics["mean"]:.2f}
Stddev:  {self.free_capacity_inbound_statistics["stddev"]:.2f}
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: {self.free_capacity_outbound_statistics["minimum"]:.2f}
Maximum: {self.free_capacity_outbound_statistics["maximum"]:.2f}
Mean:    {self.free_capacity_outbound_statistics["mean"]:.2f}
Stddev:  {self.free_capacity_outbound_statistics["stddev"]:.2f}
(rounding errors might exist)
"""
        return report
