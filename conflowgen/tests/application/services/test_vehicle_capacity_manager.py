import datetime
import unittest

import parameterized

from conflowgen.application.services.vehicle_capacity_manager import VehicleCapacityManager
from conflowgen.descriptive_datatypes import FlowDirection
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import Train, LargeScheduledVehicle, Truck, Feeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleCapacityManager(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Container,
            Schedule,
            LargeScheduledVehicle,
            Train,
            Destination,
            Truck,
            Feeder,
        ])

        self.vehicle_capacity_manager = VehicleCapacityManager()
        self.vehicle_capacity_manager.set_transportation_buffer(transportation_buffer=0)

        schedule_train = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestServiceTrain",
            vehicle_arrives_at=datetime.date(year=2024, month=5, day=26),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_inbound_container_volume=90,
        )
        self.train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            inbound_container_volume=30,
            scheduled_arrival=datetime.datetime(year=2024, month=5, day=26, hour=13, minute=15),
            schedule=schedule_train
        )
        self.train = Train.create(
            large_scheduled_vehicle=self.train_lsv
        )

        schedule_feeder = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestServiceFeeder",
            vehicle_arrives_at=datetime.date(year=2024, month=5, day=26),
            vehicle_arrives_at_time=datetime.time(hour=11, minute=15),
            average_vehicle_capacity=1200,
            average_inbound_container_volume=600,
        )
        self.feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=1200,
            inbound_container_volume=600,
            scheduled_arrival=datetime.datetime(year=2024, month=5, day=26, hour=11, minute=45),
            schedule=schedule_feeder
        )
        self.feeder = Feeder.create(
            large_scheduled_vehicle=self.feeder_lsv
        )

    @parameterized.parameterized.expand([
        [FlowDirection.export_flow],
        [FlowDirection.transshipment_flow]
    ])
    def test_free_capacity_on_outbound_journey_without_any_containers_and_no_ramp_up_period(
            self, flow_direction: FlowDirection
    ):
        """
        Independent of the flow direction, the outbound capacity should not change as long as no ramp-up period is
        defined.
        """
        free_capacity_on_train = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.train, flow_direction
        )
        self.assertEqual(free_capacity_on_train, 30)

        free_capacity_on_feeder = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.feeder, flow_direction
        )
        self.assertEqual(free_capacity_on_feeder, 600)


    @parameterized.parameterized.expand([
        [FlowDirection.import_flow, 30, 600],
        [FlowDirection.export_flow, 30, 600],
        [FlowDirection.transshipment_flow, 6, 120],  # downscale by 20%
    ])
    def test_free_capacity_on_outbound_journey_without_any_containers_and_a_ramp_up_period(
            self, flow_direction: FlowDirection, train_volume: int, feeder_volume: int
    ):
        """
        The outbound capacity should change for transshipment when a ramp-up period is defined and is applicable.
        """
        self.vehicle_capacity_manager.set_ramp_up_and_down_times(
            ramp_up_period_end=datetime.datetime(year=2024, month=5, day=27)  # one day after the feeder and train
        )
        train_volume_calc = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.train, flow_direction
        )
        self.assertEqual(
            train_volume, train_volume_calc, f"The used TEU capacity of the train is {train_volume} TEU."
        )

        feeder_volume_calc = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.feeder, flow_direction
        )
        self.assertEqual(
            feeder_volume, feeder_volume_calc, f"The used TEU capacity of the feeder is {feeder_volume} TEU."
        )

    def test_free_capacity_on_inbound_journey_without_any_containers_and_no_ramp_down_period(self):
        """
        Independent of the flow direction, the inbound capacity should not change as long as no ramp-down period is
        defined.
        """
        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_inbound_journey(
            self.train
        )
        self.assertEqual(free_capacity_in_teu, 30, "The used TEU capacity of the train is 30 TEU.")

        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_inbound_journey(
            self.feeder
        )
        self.assertEqual(free_capacity_in_teu, 600, "The used TEU capacity of the feeder is 600 TEU.")

    def test_free_capacity_on_inbound_journey_without_any_containers_and_a_ramp_down_period(self):
        """
        Independent of the flow direction, the inbound capacity is capped during the ramp-down period.
        """
        self.vehicle_capacity_manager.set_ramp_up_and_down_times(
            ramp_down_period_start=datetime.datetime(year=2024, month=5, day=25)  # one day before the feeder and train
        )

        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_inbound_journey(
            self.train
        )
        self.assertEqual(
            free_capacity_in_teu, 6, "The used TEU capacity of the train is 20% of 30 TEU."
        )

        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_inbound_journey(
            self.feeder
        )
        self.assertEqual(
            free_capacity_in_teu, 120, "The used TEU capacity of the feeder is 20% of 600 TEU."
        )

    def test_free_capacity_for_one_teu(self):
        """No ramp-up or ramp-down period applied"""
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.train, FlowDirection.undefined
        )
        self.assertEqual(
            free_capacity_in_teu, 29, "The used TEU capacity of the train is 30 TEU, and 1 TEU is used by "
                                      "the one container we just created.")

    def test_free_capacity_during_ramp_up_period_for_one_teu(self):
        Container.create(
            weight=20,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=self.feeder_lsv,
        )
        self.vehicle_capacity_manager.set_ramp_up_and_down_times(
            # one day after the feeder
            ramp_up_period_end=datetime.datetime(year=2024, month=5, day=27)
        )
        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.feeder, FlowDirection.transshipment_flow
        )
        self.assertAlmostEqual(free_capacity_in_teu, 118, msg="20% of 600 TEU is 120, of that 2 TEU minus")

    def test_free_capacity_during_ramp_down_period_for_one_teu(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.train,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=self.train_lsv,
        )
        self.vehicle_capacity_manager.set_ramp_up_and_down_times(
            # one day before the train
            ramp_down_period_start=datetime.datetime(year=2024, month=5, day=25)
        )
        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_inbound_journey(
            self.train
        )
        self.assertAlmostEqual(
            free_capacity_in_teu, 5.0, msg="20% of 30 TEU is 6 TEU, of that 1 TEU is used "
        )

    def test_free_capacity_during_ramp_up_period_without_load(self):
        self.vehicle_capacity_manager.set_ramp_up_and_down_times(
            # one day before the train
            ramp_down_period_start=datetime.datetime(year=2024, month=5, day=25)
        )
        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_inbound_journey(
            self.train
        )
        self.assertAlmostEqual(free_capacity_in_teu, 6)

    def test_free_capacity_for_one_ffe(self):
        Container.create(
            weight=20,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.train,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.train, FlowDirection.undefined
        )
        self.assertEqual(free_capacity_in_teu, 28)  # 30 - 2.5

    def test_free_capacity_for_45_foot_container(self):
        Container.create(
            weight=20,
            length=ContainerLength.forty_five_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.train, FlowDirection.undefined
        )
        self.assertEqual(free_capacity_in_teu, 27.75, "A 45' container uses 2.25 TEU")

    def test_free_capacity_for_other_container(self):
        Container.create(
            weight=20,
            length=ContainerLength.other,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.vehicle_capacity_manager.get_free_capacity_for_outbound_journey(
            self.train, FlowDirection.undefined
        )
        self.assertEqual(free_capacity_in_teu, 27.5, "30 TEU minus 2.5 TEU")
