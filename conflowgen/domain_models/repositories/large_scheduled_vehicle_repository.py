from typing import Dict, List, Type

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, AbstractLargeScheduledVehicle


class LargeScheduledVehicleRepository:

    @staticmethod
    def load_all_vehicles() -> Dict[ModeOfTransport, List[Type[AbstractLargeScheduledVehicle]]]:
        result = {}
        for vehicle_type in ModeOfTransport.get_scheduled_vehicles():
            large_schedule_vehicle_as_subtype = AbstractLargeScheduledVehicle.map_mode_of_transport_to_class(
                vehicle_type)
            result[vehicle_type] = list(large_schedule_vehicle_as_subtype.select().join(LargeScheduledVehicle))
        return result
