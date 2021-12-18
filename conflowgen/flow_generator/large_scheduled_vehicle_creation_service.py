import datetime
from typing import List
import logging

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.factories.container_factory import ContainerFactory
from conflowgen.domain_models.factories.fleet_factory import FleetFactory
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import AbstractLargeScheduledVehicle


class LargeScheduledVehicleCreationService:
    def __init__(self):
        self.logger = logging.getLogger("conflowgen")
        fleet_factory = FleetFactory()
        self.vehicle_factory = fleet_factory.vehicle_factory
        self.fleet_creator = {
            ModeOfTransport.train: fleet_factory.create_train_fleet,
            ModeOfTransport.feeder: fleet_factory.create_feeder_fleet,
            ModeOfTransport.deep_sea_vessel: fleet_factory.create_deep_sea_vessel_fleet,
            ModeOfTransport.barge: fleet_factory.create_barge_fleet
        }
        self.container_factory = ContainerFactory()
        self.container_flow_start_date = None
        self.container_flow_end_date = None

    def reload_properties(
            self,
            container_flow_start_date: datetime.date,
            container_flow_end_date: datetime.date
    ):
        assert container_flow_start_date < container_flow_end_date
        self.container_flow_start_date = container_flow_start_date
        self.container_flow_end_date = container_flow_end_date
        self.container_factory.reload_distributions()

    def create(self) -> None:
        assert self.container_flow_start_date is not None
        assert self.container_flow_end_date is not None
        schedules: List[Schedule] = Schedule.select().execute()  # pylint: disable=no-value-for-parameter
        for i, schedule in enumerate(schedules):
            self.logger.debug(f"Create vehicles and containers for service '{schedule.service_name}' of type "
                              f"'{schedule.vehicle_type}', "
                              f"progress: {i+1} / {len(schedules)} ({100*(i + 1)/len(schedules):.2f}%)")
            # noinspection PyArgumentList
            vehicles: List[AbstractLargeScheduledVehicle] = self.fleet_creator[schedule.vehicle_type](
                schedule=schedule,
                latest_at=self.container_flow_end_date,
                first_at=self.container_flow_start_date
            )
            for vehicle in vehicles:
                self.container_factory.create_containers_for_large_scheduled_vehicle(vehicle)
