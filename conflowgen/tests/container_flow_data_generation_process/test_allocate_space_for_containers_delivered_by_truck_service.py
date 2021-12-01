import datetime
import unittest

from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder, \
    container_length_distribution_seeder, container_weight_distribution_seeder, \
    container_storage_requirement_distribution_seeder
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Train, Barge, Feeder, DeepSeaVessel, Truck, \
    AbstractLargeScheduledVehicle
from conflowgen.container_flow_data_generation_process.allocate_space_for_containers_delivered_by_truck_service import \
    AllocateSpaceForContainersDeliveredByTruckService
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestAllocateSpaceForContainersDeliveredByTruckService(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Schedule,
            LargeScheduledVehicle,
            Train,
            Barge,
            Feeder,
            DeepSeaVessel,
            Container,
            Truck,
            TruckArrivalInformationForDelivery,
            TruckArrivalInformationForPickup,
            Destination,
            ModeOfTransportDistribution,
            ContainerLengthDistribution,
            ContainerWeightDistribution,
            StorageRequirementDistribution
        ])

        mode_of_transport_distribution_seeder.seed()
        container_length_distribution_seeder.seed()
        container_weight_distribution_seeder.seed()
        container_storage_requirement_distribution_seeder.seed()

        self.service = AllocateSpaceForContainersDeliveredByTruckService()
        self.service.reload_distribution(
            transportation_buffer=0
        )

        # Enables visualisation, helpful for probability distributions
        # However, this blocks the execution of tests.
        self.debug = False

    @staticmethod
    def _create_feeder(scheduled_arrival: datetime.datetime) -> Feeder:
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=scheduled_arrival.date(),
            vehicle_arrives_at_time=scheduled_arrival.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
        )
        schedule.save()
        feeder_lsv = LargeScheduledVehicle.create(
            capacity_in_teu=schedule.average_vehicle_capacity,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        feeder_lsv.save()
        feeder = Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        feeder.save()
        return feeder

    @staticmethod
    def _create_train(scheduled_arrival: datetime.datetime) -> Train:
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestTrainService",
            vehicle_arrives_at=scheduled_arrival.date(),
            vehicle_arrives_at_time=scheduled_arrival.time(),
            average_vehicle_capacity=90,
            average_moved_capacity=90,
        )
        schedule.save()
        train_lsv = LargeScheduledVehicle.create(
            capacity_in_teu=96,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        train_lsv.save()
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
        container.save()
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
        container.save()
        return container

    def test_does_nothing_if_no_vehicle_is_available(self):
        now = datetime.datetime.now()
        truck = self._create_truck(arrival=now)
        container = self._create_container_for_truck(truck)
        self.assertIsNone(self.service.allocate())
        containers = Container.select().execute()
        self.assertIn(container, containers)
        self.assertEqual(1, len(containers))

    def test_happy_path(self):
        now = datetime.datetime.now()
        feeder = self._create_feeder(scheduled_arrival=now + datetime.timedelta(days=1))

        # The import container already exists
        container = Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=feeder.large_scheduled_vehicle,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )
        container.save()

        # due to the existing import container, one export container must be generated
        self.assertEqual(self.service._get_number_containers_to_allocate(), 1)

        # that export container is generated now
        self.assertIsNone(self.service.allocate())

        containers = Container.select().execute()
        self.assertIn(container, containers)
        self.assertEqual(2, len(containers))
        created_container = (set(containers) - {container}).pop()
        self.assertTrue(created_container.delivered_by, ModeOfTransport.truck)
        self.assertTrue(created_container.picked_up_by_large_scheduled_vehicle, feeder.large_scheduled_vehicle)
