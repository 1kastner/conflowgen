import datetime
import unittest

import parameterized

from conflowgen.descriptive_datatypes import FlowDirection
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.application.services.vehicle_container_volume_calculator import VehicleContainerVolumeCalculator
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, DeepSeaVessel, Feeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleContainerVolumeCalculator(unittest.TestCase):

    def setUp(self) -> None:
        """Create database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            LargeScheduledVehicle,
            Schedule,
            DeepSeaVessel,
            Feeder,
        ])
        self.calculator = VehicleContainerVolumeCalculator()
        self.calculator.set_transportation_buffer(0)

        schedule_deep_sea_vessel = Schedule.create(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name="TestService-DeepSeaVessel",
            vehicle_arrives_at=datetime.date(year=2024, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=12000,
            average_inbound_container_volume=3000,
        )
        self.lsv_deep_sea_vessel = LargeScheduledVehicle.create(
            vehicle_name="TestShip-DeepSeaVessel-1",
            capacity_in_teu=12000,
            inbound_container_volume=3000,
            scheduled_arrival=datetime.datetime(year=2024, month=8, day=7, hour=13, minute=15),
            schedule=schedule_deep_sea_vessel
        )
        self.deep_sea_vessel = DeepSeaVessel.create(
            large_scheduled_vehicle=self.lsv_deep_sea_vessel
        )

        schedule_feeder = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestService-Feeder",
            vehicle_arrives_at=datetime.date(year=2024, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=1200,
            average_inbound_container_volume=600,
        )
        self.lsv_feeder = LargeScheduledVehicle.create(
            vehicle_name="TestShip-Feeder1",
            capacity_in_teu=1200,
            inbound_container_volume=600,
            scheduled_arrival=datetime.datetime(year=2024, month=8, day=7, hour=11, minute=9),
            schedule=schedule_feeder
        )
        self.feeder = Feeder.create(
            large_scheduled_vehicle=self.lsv_feeder
        )

    @parameterized.parameterized.expand([
        [flow_direction] for flow_direction in FlowDirection
    ])
    def test_get_maximum_transported_container_volume_on_outbound_journey_and_no_ramp_up_period(
            self, flow_direction: FlowDirection
    ):
        """
        Independent of the flow direction, the outbound capacity should not change as long as no ramp-up period is
        defined.
        """
        feeder_vessel_calc = self.calculator.get_maximum_transported_container_volume_on_outbound_journey(
            self.lsv_feeder, flow_direction
        )
        scaled_moved_container_volume, unscaled_moved_container_volume = feeder_vessel_calc
        self.assertEqual(scaled_moved_container_volume, 600)

        deep_sea_vessel_calc = self.calculator.get_maximum_transported_container_volume_on_outbound_journey(
            self.deep_sea_vessel, flow_direction
        )
        scaled_moved_container_volume, unscaled_moved_container_volume = deep_sea_vessel_calc
        self.assertEqual(scaled_moved_container_volume, 3000)


    @parameterized.parameterized.expand([
        [FlowDirection.import_flow, 600, 3000],  # normal values
        [FlowDirection.export_flow, 600, 3000],  # normal values
        [FlowDirection.transshipment_flow, 120, 600],  # downscaled by 20%
    ])
    def test_get_maximum_transported_container_volume_on_outbound_journey_and_an_applicable_ramp_up_period(
            self, flow_direction: FlowDirection, feeder_volume: int, deep_sea_volume: int
    ):
        """
        The outbound capacity should change for transshipment when a ramp-up period is defined and is applicable.
        """
        self.calculator.set_ramp_up_and_down_times(
            ramp_up_period_end=datetime.datetime(year=2024, month=8, day=8)  # one day after the two vessels
        )
        volume_feeder = self.calculator.get_maximum_transported_container_volume_on_outbound_journey(
            self.feeder, flow_direction
        )
        scaled_moved_container_volume, unscaled_moved_container_volume = volume_feeder
        self.assertEqual(scaled_moved_container_volume, feeder_volume)

        volume_deep_sea_vessel = self.calculator.get_maximum_transported_container_volume_on_outbound_journey(
            self.deep_sea_vessel, flow_direction
        )
        scaled_moved_container_volume, unscaled_moved_container_volume = volume_deep_sea_vessel
        self.assertEqual(scaled_moved_container_volume, deep_sea_volume)

    @parameterized.parameterized.expand([
        [FlowDirection.import_flow, 600, 3000],
        [FlowDirection.export_flow, 600, 3000],
        [FlowDirection.transshipment_flow, 600, 3000],
    ])
    def test_get_maximum_transported_container_volume_on_outbound_journey_and_a_non_applicable_ramp_up_period(
            self, flow_direction: FlowDirection, feeder_volume: int, deep_sea_volume: int
    ):
        """
        The outbound capacity should not change for transshipment when a ramp-up period is defined but lies in the past.
        """
        self.calculator.set_ramp_up_and_down_times(
            ramp_up_period_end=datetime.datetime(year=2024, month=8, day=6)  # one day after the two vessels
        )
        feeder_volume_calc = self.calculator.get_maximum_transported_container_volume_on_outbound_journey(
            self.feeder, flow_direction
        )
        scaled_moved_container_volume, unscaled_moved_container_volume = feeder_volume_calc
        self.assertEqual(scaled_moved_container_volume, feeder_volume)

        deep_sea_volume_calc = self.calculator.get_maximum_transported_container_volume_on_outbound_journey(
            self.deep_sea_vessel, flow_direction
        )
        scaled_moved_container_volume, unscaled_moved_container_volume = deep_sea_volume_calc
        self.assertEqual(scaled_moved_container_volume, deep_sea_volume)


    def test_get_transported_container_volume_on_inbound_journey_and_no_ramp_down_period(self):
        """
        Independent of the flow direction, the inbound capacity should not change as long as no ramp-down period is
        defined.
        """
        feeder_volume_calc = self.calculator.get_transported_container_volume_on_inbound_journey(
            self.feeder
        )
        self.assertEqual(feeder_volume_calc, 600)

        deep_sea_vessel_calc = self.calculator.get_transported_container_volume_on_inbound_journey(
            self.deep_sea_vessel
        )
        self.assertEqual(deep_sea_vessel_calc, 3000)

    def test_get_transported_container_volume_on_inbound_journey_and_an_applicable_ramp_down_period(self):
        """
        Independent of the flow direction, the inbound capacity is capped during the ramp-down period.
        """
        self.calculator.set_ramp_up_and_down_times(
            ramp_down_period_start=datetime.datetime(year=2021, month=8, day=6)  # one day before the feeder and train
        )

        feeder_vessel_calc = self.calculator.get_transported_container_volume_on_inbound_journey(
            self.lsv_feeder
        )
        self.assertEqual(feeder_vessel_calc, 120, "Downscaled by 20%")

        deep_sea_vessel_calc = self.calculator.get_transported_container_volume_on_inbound_journey(
            self.lsv_deep_sea_vessel
        )
        self.assertEqual(deep_sea_vessel_calc, 600, "Downscaled by 20%")

    def test_get_transported_container_volume_on_inbound_journey_and_a_non_applicable_ramp_down_period(self):
        """
        Independent of the flow direction, the inbound capacity is capped during the ramp-down period.
        """
        self.calculator.set_ramp_up_and_down_times(
            ramp_down_period_start=datetime.datetime(year=2024, month=8, day=8)  # one day after
        )

        feeder_volume_calc = self.calculator.get_transported_container_volume_on_inbound_journey(
            self.lsv_feeder
        )
        self.assertEqual(feeder_volume_calc, 600, "Nothing should be downscaled")

        deep_sea_vessel_volume_calc = self.calculator.get_transported_container_volume_on_inbound_journey(
            self.lsv_deep_sea_vessel
        )
        self.assertEqual(deep_sea_vessel_volume_calc, 3000, "Nothing should be downscaled")
