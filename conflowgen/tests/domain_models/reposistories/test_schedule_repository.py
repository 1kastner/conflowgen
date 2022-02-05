import datetime
import unittest
import unittest.mock

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.repositories.schedule_repository import ScheduleRepository
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Train, Barge, Feeder, DeepSeaVessel, Truck
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestScheduleRepository(unittest.TestCase):

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
            Destination
        ])
        self.schedule_repository = ScheduleRepository()
        self.schedule_repository.set_transportation_buffer(transportation_buffer=0)

    def test_empty_schedule_database_throws_no_exception(self):
        vehicles_and_frequency = self.schedule_repository.get_departing_vehicles(
            datetime.datetime.now(),
            datetime.datetime.now() + datetime.timedelta(days=21),
            vehicle_type=ModeOfTransport.train,
            required_capacity=ContainerLength.twenty_feet
        )

        self.assertEqual(len(vehicles_and_frequency), 0)

    def test_find_vehicle_if_in_time_range(self):
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestTrainService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_moved_capacity=1,
        )
        train_moves_this_capacity = 7
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            moved_capacity=train_moves_this_capacity,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        train_lsv.save()
        train = Train.create(
            large_scheduled_vehicle=train_lsv
        )
        train.save()

        vehicles = self.schedule_repository.get_departing_vehicles(
            start=datetime.datetime(year=2021, month=8, day=5, hour=0, minute=0),
            end=datetime.datetime(year=2021, month=8, day=10, hour=23, minute=59),
            vehicle_type=ModeOfTransport.train,
            required_capacity=ContainerLength.twenty_feet
        )

        self.assertEqual(len(vehicles), 1)

    def test_export_buffer_below_capacity(self):
        self.schedule_repository = ScheduleRepository()
        self.schedule_repository.set_transportation_buffer(transportation_buffer=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestTrainService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_moved_capacity=1,
        )
        train_moves_this_capacity = 7
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            moved_capacity=train_moves_this_capacity,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        train_lsv.save()
        train = Train.create(
            large_scheduled_vehicle=train_lsv
        )
        train.save()

        vehicles = self.schedule_repository.get_departing_vehicles(
            start=datetime.datetime(year=2021, month=8, day=5, hour=0, minute=0),
            end=datetime.datetime(year=2021, month=8, day=10, hour=23, minute=59),
            vehicle_type=ModeOfTransport.train,
            required_capacity=ContainerLength.twenty_feet
        )
        self.assertEqual(len(vehicles), 1)

    def test_export_buffer_above_capacity(self):
        self.schedule_repository = ScheduleRepository()
        self.schedule_repository.set_transportation_buffer(transportation_buffer=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestTrainService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=4,
            average_moved_capacity=2,
        )
        train_moves_this_capacity = 7
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=8,
            moved_capacity=train_moves_this_capacity,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        train_lsv.save()
        train = Train.create(
            large_scheduled_vehicle=train_lsv
        )
        train.save()

        vehicles = self.schedule_repository.get_departing_vehicles(
            start=datetime.datetime(year=2021, month=8, day=5, hour=0, minute=0),
            end=datetime.datetime(year=2021, month=8, day=10, hour=23, minute=59),
            vehicle_type=ModeOfTransport.train,
            required_capacity=ContainerLength.twenty_feet
        )

        self.assertEqual(len(vehicles), 1)

    def test_ignore_vehicle_outside_time_range(self):
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_moved_capacity=1,
        )
        train_moves_this_capacity = 7
        train = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            moved_capacity=train_moves_this_capacity,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        train.save()

        vehicles_and_frequency = self.schedule_repository.get_departing_vehicles(
            start=datetime.datetime(year=2021, month=8, day=10, hour=13, minute=15),
            end=datetime.datetime(year=2021, month=8, day=15, hour=13, minute=15),
            vehicle_type=ModeOfTransport.train,
            required_capacity=ContainerLength.forty_feet
        )

        self.assertEqual(len(vehicles_and_frequency), 0)

    def test_check_used_20_foot_containers(self):
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_moved_capacity=90,
        )
        train_moves_this_capacity_in_teu = 2
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            moved_capacity=train_moves_this_capacity_in_teu,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        train_lsv.save()
        train = Train.create(
            large_scheduled_vehicle=train_lsv
        )
        train.save()

        # This container is already loaded on the train
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.train,
            picked_up_by_large_scheduled_vehicle=train_lsv,
        )
        available_vehicles = self.schedule_repository.get_departing_vehicles(
            start=datetime.datetime(year=2021, month=8, day=5, hour=0, minute=0),
            end=datetime.datetime(year=2021, month=8, day=10, hour=23, minute=59),
            vehicle_type=ModeOfTransport.train,
            required_capacity=ContainerLength.twenty_feet
        )

        self.assertEqual(len(available_vehicles), 1)
        self.assertIn(train, available_vehicles)

    def test_check_used_40_foot_containers(self):
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_moved_capacity=90,
        )
        train_moves_this_capacity_in_teu = 3
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            moved_capacity=train_moves_this_capacity_in_teu,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        train_lsv.save()
        train = Train.create(
            large_scheduled_vehicle=train_lsv
        )
        train.save()

        # This container is already loaded on the train
        Container.create(
            weight=20,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.train,
            picked_up_by_large_scheduled_vehicle=train_lsv
        )
        vehicles = self.schedule_repository.get_departing_vehicles(
            start=datetime.datetime(year=2021, month=8, day=5, hour=0, minute=0),
            end=datetime.datetime(year=2021, month=8, day=10, hour=23, minute=59),
            vehicle_type=ModeOfTransport.train,
            required_capacity=ContainerLength.twenty_feet
        )

        self.assertEqual(len(vehicles), 1)

    def test_use_lsv_repository(self):
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_moved_capacity=90,
        )
        train_moves_this_capacity_in_teu = 3
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            moved_capacity=train_moves_this_capacity_in_teu,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        train_lsv.save()
        train = Train.create(
            large_scheduled_vehicle=train_lsv
        )
        train.save()

        # This container is already loaded on the train
        Container.create(
            weight=20,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.train,
            picked_up_by_large_scheduled_vehicle=train_lsv,
        )

        with unittest.mock.patch.object(
                self.schedule_repository.large_scheduled_vehicle_repository,
                'get_free_capacity_for_outbound_journey',
                return_value=1) as mock_method:
            self.schedule_repository.get_departing_vehicles(
                start=datetime.datetime(year=2021, month=8, day=5, hour=0, minute=0),
                end=datetime.datetime(year=2021, month=8, day=10, hour=23, minute=59),
                vehicle_type=ModeOfTransport.train,
                required_capacity=ContainerLength.twenty_feet
            )
        mock_method.assert_called_once_with(train)
