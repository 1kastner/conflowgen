import datetime
import unittest

from conflowgen.application.models.random_seed_store import RandomSeedStore
from conflowgen.flow_generator.assign_destination_to_container_service import \
    AssignDestinationToContainerService
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_repositories.container_destination_distribution_repository import \
    ContainerDestinationDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Train, Feeder, DeepSeaVessel, Truck, \
    AbstractLargeScheduledVehicle
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestAssignDestinationToContainerService(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Schedule,
            LargeScheduledVehicle,
            Container,
            Destination,
            TruckArrivalInformationForDelivery,
            TruckArrivalInformationForPickup,
            Truck,
            Feeder,
            DeepSeaVessel,
            ModeOfTransportDistribution,
            RandomSeedStore,
        ])
        self.repository = ContainerDestinationDistributionRepository()
        self.service = AssignDestinationToContainerService()

    @staticmethod
    def _create_feeder(scheduled_arrival: datetime.datetime) -> Feeder:
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=scheduled_arrival.date(),
            vehicle_arrives_at_time=scheduled_arrival.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
        )
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=schedule.average_vehicle_capacity,
            inbound_container_volume=schedule.average_inbound_container_volume,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        feeder = Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        return feeder

    @staticmethod
    def _create_train(scheduled_arrival: datetime.datetime) -> Train:
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestTrainService",
            vehicle_arrives_at=scheduled_arrival.date(),
            vehicle_arrives_at_time=scheduled_arrival.time(),
            average_vehicle_capacity=90,
            average_inbound_container_volume=90,
        )
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=96,
            inbound_container_volume=schedule.average_inbound_container_volume,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        train = Train.create(
            large_scheduled_vehicle=train_lsv
        )
        train.save()
        return train

    @staticmethod
    def _create_truck(arrival: datetime.datetime) -> Truck:
        ati = TruckArrivalInformationForDelivery.create(
            realized_container_delivery_time=arrival,
            planned_container_delivery_time_at_window_start=None
        )
        truck = Truck.create(
            delivers_container=False,
            picks_up_container=True,
            truck_arrival_information_for_delivery=ati
        )
        truck.save()
        return truck

    @staticmethod
    def _create_container_for_truck(truck: Truck):
        container = Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            delivered_by_truck=truck,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.feeder
        )
        return container

    @staticmethod
    def _create_container_for_large_scheduled_vehicle(vehicle: AbstractLargeScheduledVehicle):
        large_scheduled_vehicle = vehicle.large_scheduled_vehicle
        vehicle_type = vehicle.get_mode_of_transport()
        container = Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=vehicle_type,
            delivered_by_large_scheduled_vehicle=large_scheduled_vehicle,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.feeder
        )
        return container

    def test_no_exception_for_empty_database(self):
        self.service.assign()

    def test_load_container_from_truck_onto_feeder(self):
        truck = self._create_truck(datetime.datetime(year=2021, month=8, day=5, hour=9, minute=0))
        feeder = self._create_feeder(datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15))
        container = self._create_container_for_truck(truck)
        container.picked_up_by_large_scheduled_vehicle = feeder.large_scheduled_vehicle
        container.save()

        schedule = feeder.large_scheduled_vehicle.schedule
        destination_1 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=1,
            destination_name="TestDestination1",
        )
        destination_2 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=2,
            destination_name="TestDestination2",
        )

        distribution = {
            schedule: {
                destination_1: 0.4,
                destination_2: 0.6
            }
        }
        self.repository.set_distribution(distribution)
        self.service.reload_distributions()

        self.service.assign()

        container_update: Container = Container.get_by_id(container.id)

        self.assertIn(container_update.destination, (destination_1, destination_2))

    def test_wrong_direction(self):
        truck = self._create_truck(datetime.datetime(year=2021, month=8, day=5, hour=9, minute=0))
        feeder = self._create_feeder(datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15))
        container = self._create_container_for_large_scheduled_vehicle(feeder)
        container.picked_up_by_large_scheduled_vehicle = None
        container.picked_up_by_truck = truck
        container.picked_up_by = ModeOfTransport.truck
        container.save()

        schedule = feeder.large_scheduled_vehicle.schedule
        destination_1 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=1,
            destination_name="TestDestination1",
        )
        destination_2 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=2,
            destination_name="TestDestination2",
        )

        distribution = {
            schedule: {
                destination_1: 0.4,
                destination_2: 0.6
            }
        }
        self.repository.set_distribution(distribution)
        self.service.reload_distributions()

        self.service.assign()

        container_update: Container = Container.get_by_id(container.id)

        self.assertIsNone(container_update.destination)
