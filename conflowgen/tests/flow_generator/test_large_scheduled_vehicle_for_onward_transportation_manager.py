import datetime
import unittest
from typing import Iterable

from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder, \
    container_dwell_time_distribution_seeder
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Train, Barge, Feeder, DeepSeaVessel, Truck, \
    AbstractLargeScheduledVehicle
from conflowgen.flow_generator.large_scheduled_vehicle_for_onward_transportation_manager \
    import LargeScheduledVehicleForOnwardTransportationManager
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestLargeScheduledVehicleForExportContainersManager(unittest.TestCase):

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
            ContainerDwellTimeDistribution,
        ])

        mode_of_transport_distribution_seeder.seed()
        container_dwell_time_distribution_seeder.seed()

        self.manager = LargeScheduledVehicleForOnwardTransportationManager()
        self.manager.reload_properties(
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
            vehicle_name="TestFeeder1",
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
            vehicle_name="TestTrain1",
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
        self.assertIsNone(self.manager.choose_departing_vehicle_for_containers())

    def test_load_container_from_truck_on_feeder(self):
        truck = self._create_truck(datetime.datetime(year=2021, month=8, day=5, hour=9, minute=0))
        feeder = self._create_feeder(datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15))

        container = self._create_container_for_truck(truck)

        self.manager.choose_departing_vehicle_for_containers()

        self.assertIsNone(container.picked_up_by_large_scheduled_vehicle, msg="peewee does not use a singleton pattern")
        self.assertEqual(Container.select().count(), 1)
        container_reloaded = Container.get()
        self.assertEqual(feeder.large_scheduled_vehicle, container_reloaded.picked_up_by_large_scheduled_vehicle,
                         msg="Only after reloading the container transfer information is available.")

    def test_do_not_overload_feeder_with_truck_traffic(self):
        truck = self._create_truck(datetime.datetime(year=2021, month=8, day=5, hour=9, minute=0))
        feeder = self._create_feeder(datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15))
        feeder.large_scheduled_vehicle.moved_capacity = 10  # in TEU
        containers = [self._create_container_for_truck(truck) for _ in range(10)]
        self.assertEqual(Container.select().count(), 10)
        teu_generated = sum([ContainerLength.get_factor(container.length) for container in containers])
        self.assertGreaterEqual(teu_generated, 10, "Generating 10 containers with each at least 1 TEU must result in a "
                                                   "total TEU of more than 10 TEU")

        self.manager.choose_departing_vehicle_for_containers()

        containers_reloaded = Container.select().where(
            Container.picked_up_by_large_scheduled_vehicle == feeder
        )
        self.assertTrue(set(containers_reloaded).issubset(set(containers)), "Feeder must only load generated "
                                                                            "containers")
        teu_loaded = 0
        for container in containers_reloaded:  # pylint: disable=E1133
            self.assertEqual(container.picked_up_by_large_scheduled_vehicle, feeder.large_scheduled_vehicle)
            teu_loaded += ContainerLength.get_factor(container.length)
        self.assertLessEqual(teu_loaded, 10, "Feeder must not be loaded with more than 10 TEU")

    def test_do_not_overload_feeder_with_train_traffic(self):
        train = self._create_train(datetime.datetime(year=2021, month=8, day=5, hour=9, minute=0))
        containers = [
            self._create_container_for_large_scheduled_vehicle(train)
            for _ in range(train.large_scheduled_vehicle.moved_capacity)  # here only 20' containers
        ]

        feeder = self._create_feeder(datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15))
        feeder.large_scheduled_vehicle.moved_capacity = 80  # in TEU
        feeder.save()

        self.assertEqual(Container.select().count(), 90)
        teu_generated = sum([ContainerLength.get_factor(container.length) for container in containers])
        self.assertEqual(teu_generated, 90)

        self.manager.choose_departing_vehicle_for_containers()

        containers_reloaded: Iterable[Container] = Container.select().where(
            Container.picked_up_by_large_scheduled_vehicle == feeder
        )
        self.assertTrue(set(containers_reloaded).issubset(set(containers)), "Feeder must only load generated "
                                                                            "containers")
        teu_loaded = 0
        for container in containers_reloaded:  # pylint: disable=not-an-iterable
            self.assertEqual(container.picked_up_by_large_scheduled_vehicle, feeder.large_scheduled_vehicle)
            teu_loaded += ContainerLength.get_factor(container.length)
        self.assertLessEqual(teu_loaded, 80, "Feeder must not be loaded with more than what it can carry")

    def test_do_not_overload_feeder_with_train_traffic_of_two_vehicles(self):
        train_1 = self._create_train(datetime.datetime(year=2021, month=8, day=5, hour=9, minute=0))
        train_2 = self._create_train(datetime.datetime(year=2021, month=8, day=5, hour=15, minute=0))
        containers_1 = [
            self._create_container_for_large_scheduled_vehicle(train_1)
            for _ in range(train_1.large_scheduled_vehicle.moved_capacity)  # here only 20' containers
        ]
        containers_2 = [
            self._create_container_for_large_scheduled_vehicle(train_2)
            for _ in range(train_2.large_scheduled_vehicle.moved_capacity)  # here only 20' containers
        ]
        containers = containers_1 + containers_2

        feeder = self._create_feeder(datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15))
        feeder.large_scheduled_vehicle.moved_capacity = 80  # in TEU
        feeder.save()

        self.assertEqual(Container.select().count(), 180)
        teu_generated = sum([ContainerLength.get_factor(container.length) for container in containers])
        self.assertEqual(teu_generated, 180)

        self.manager.choose_departing_vehicle_for_containers()

        containers_reloaded: Iterable[Container] = Container.select().where(
            Container.picked_up_by_large_scheduled_vehicle == feeder
        )
        self.assertTrue(set(containers_reloaded).issubset(set(containers)), "Feeder must only load generated "
                                                                            "containers")
        teu_loaded = 0
        for container in containers_reloaded:   # pylint: disable=not-an-iterable
            self.assertEqual(container.picked_up_by_large_scheduled_vehicle, feeder.large_scheduled_vehicle)
            teu_loaded += ContainerLength.get_factor(container.length)
        self.assertLessEqual(teu_loaded, 80, "Feeder must not be loaded with more than what it can carry")

    def test_do_not_overload_feeder_with_train_traffic_of_two_vehicles_and_changing_container_lengths(self):
        train_1 = self._create_train(datetime.datetime(year=2021, month=8, day=5, hour=9, minute=0))
        train_2 = self._create_train(datetime.datetime(year=2021, month=8, day=5, hour=15, minute=0))
        containers_1 = [
            self._create_container_for_large_scheduled_vehicle(train_1)
            for _ in range(train_1.large_scheduled_vehicle.moved_capacity)  # here only 20' containers
        ]
        containers_2 = [
            self._create_container_for_large_scheduled_vehicle(train_2)
            for _ in range(train_2.large_scheduled_vehicle.moved_capacity)  # here only 20' containers
        ]
        for container in containers_2:
            container.length = ContainerLength.forty_feet
            container.save()
        containers = containers_1 + containers_2

        feeder = self._create_feeder(datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15))
        feeder.large_scheduled_vehicle.moved_capacity = 80  # in TEU
        feeder.save()

        self.assertEqual(Container.select().count(), 180)
        teu_generated = sum([ContainerLength.get_factor(container.length) for container in containers])
        self.assertEqual(teu_generated, 270)

        self.manager.choose_departing_vehicle_for_containers()

        containers_reloaded: Iterable[Container] = Container.select().where(
            Container.picked_up_by_large_scheduled_vehicle == feeder
        )
        self.assertTrue(set(containers_reloaded).issubset(set(containers)), "Feeder must only load generated "
                                                                            "containers")
        teu_loaded = 0
        for container in containers_reloaded:  # pylint: disable=not-an-iterable
            self.assertEqual(container.picked_up_by_large_scheduled_vehicle, feeder.large_scheduled_vehicle)
            teu_loaded += ContainerLength.get_factor(container.length)
        self.assertLessEqual(teu_loaded, 80, "Feeder must not be loaded with more than what it can carry")
