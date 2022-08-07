"""
Check if container weights can be properly seeded.
"""
import datetime
import unittest

from conflowgen.application.reports.container_flow_statistics_report import ContainerFlowStatisticsReport
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForPickup, \
    TruckArrivalInformationForDelivery
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, DeepSeaVessel, Feeder, Train, Barge, \
    AbstractLargeScheduledVehicle, Truck
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowStatisticsReport(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            LargeScheduledVehicle,
            DeepSeaVessel,
            Feeder,
            Train,
            Barge,
            Schedule,
            Destination,
            Container,
            Truck,
            TruckArrivalInformationForDelivery,
            TruckArrivalInformationForPickup
        ])
        self.report = ContainerFlowStatisticsReport()
        self.report.set_transportation_buffer(0.2)

    @staticmethod
    def _create_feeder(scheduled_arrival: datetime.datetime, service_name_suffix: str = "") -> Feeder:
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService" + service_name_suffix,
            vehicle_arrives_at=scheduled_arrival.date(),
            vehicle_arrives_at_time=scheduled_arrival.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
        )
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=schedule.average_vehicle_capacity,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=scheduled_arrival,
            schedule=schedule
        )
        feeder = Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        return feeder

    @staticmethod
    def _create_container_delivered_by_large_scheduled_vehicle(vehicle: AbstractLargeScheduledVehicle):
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

    @staticmethod
    def _create_truck(arrival: datetime.datetime) -> Truck:
        aid = TruckArrivalInformationForDelivery.create(
            realized_container_delivery_time=arrival
        )
        aid.save()
        aip = TruckArrivalInformationForPickup.create(
            realized_container_pickup_time=arrival
        )
        aip.save()
        truck = Truck.create(
            truck_arrival_information_for_delivery=aid,
            truck_arrival_information_for_pickup=aip,
            delivers_container=True,
            picks_up_container=True
        )
        truck.save()
        return truck

    @staticmethod
    def _create_container_delivered_by_truck(truck: Truck) -> Container:
        container = Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            delivered_by_truck=truck,
            picked_up_by_initial=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.truck
        )
        container.save()
        return container

    def test_empty_ship_using_capacity_as_maximum(self):
        now = datetime.datetime.now()
        self._create_feeder(service_name_suffix="", scheduled_arrival=now)
        truck = self._create_truck(arrival=now)
        self._create_container_delivered_by_truck(truck)
        self.report.generate()
        text = self.report.get_text_representation()
        self.assertEqual("""
Free Inbound Capacity Statistics
Minimum: 300.00
Maximum: 300.00
Mean:    300.00
Stddev:  0.00
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: 300.00
Maximum: 300.00
Mean:    300.00
Stddev:  0.00
(rounding errors might exist)
""", text, "Container should not show up here")

    def test_empty_ship_using_buffer_as_maximum(self):
        now = datetime.datetime.now()
        feeder = self._create_feeder(scheduled_arrival=now)
        feeder.large_scheduled_vehicle.moved_capacity = 20
        feeder.large_scheduled_vehicle.save()
        truck = self._create_truck(arrival=now)
        self._create_container_delivered_by_truck(truck)
        self.report.generate()
        text = self.report.get_text_representation()
        self.assertEqual("""
Free Inbound Capacity Statistics
Minimum: 20.00
Maximum: 20.00
Mean:    20.00
Stddev:  0.00
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: 24.00
Maximum: 24.00
Mean:    24.00
Stddev:  0.00
(rounding errors might exist)
""", text, "Container should not show up here")

    def test_inbound_loaded_ship_using_capacity_as_maximum(self):
        now = datetime.datetime.now()
        feeder = self._create_feeder(scheduled_arrival=now)
        feeder.large_scheduled_vehicle.moved_capacity = 20
        feeder.large_scheduled_vehicle.save()
        self._create_container_delivered_by_large_scheduled_vehicle(feeder)
        self.report.generate()
        text = self.report.get_text_representation()
        self.assertEqual("""
Free Inbound Capacity Statistics
Minimum: 19.00
Maximum: 19.00
Mean:    19.00
Stddev:  0.00
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: 24.00
Maximum: 24.00
Mean:    24.00
Stddev:  0.00
(rounding errors might exist)
""", text)

    def test_outbound_loaded_ship_using_buffer_as_maximum(self):
        now = datetime.datetime.now()
        feeder = self._create_feeder(scheduled_arrival=now)
        feeder.large_scheduled_vehicle.moved_capacity = 20
        feeder.large_scheduled_vehicle.save()
        truck = self._create_truck(arrival=now)
        container = self._create_container_delivered_by_truck(truck)
        container.picked_up_by_large_scheduled_vehicle = feeder.id  # pylint: disable=no-member
        container.picked_up_by = feeder.get_mode_of_transport()
        container.save()

        self.report.generate()
        text = self.report.get_text_representation()
        self.assertEqual("""
Free Inbound Capacity Statistics
Minimum: 20.00
Maximum: 20.00
Mean:    20.00
Stddev:  0.00
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: 23.00
Maximum: 23.00
Mean:    23.00
Stddev:  0.00
(rounding errors might exist)
""", text)

    def test_outbound_loaded_ship_using_capacity_as_maximum(self):
        now = datetime.datetime.now()
        feeder = self._create_feeder(scheduled_arrival=now)
        feeder.large_scheduled_vehicle.capacity_in_teu = 20
        feeder.large_scheduled_vehicle.moved_capacity = 20
        feeder.large_scheduled_vehicle.save()
        truck = self._create_truck(arrival=now)
        container = self._create_container_delivered_by_truck(truck)
        container.picked_up_by_large_scheduled_vehicle = feeder.id  # pylint: disable=no-member
        container.picked_up_by = feeder.get_mode_of_transport()
        container.save()

        self.report.generate()
        text = self.report.get_text_representation()
        self.assertEqual("""
Free Inbound Capacity Statistics
Minimum: 20.00
Maximum: 20.00
Mean:    20.00
Stddev:  0.00
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: 19.00
Maximum: 19.00
Mean:    19.00
Stddev:  0.00
(rounding errors might exist)
""", text)

    def test_two_ships_one_with_inbound_traffic(self):
        now = datetime.datetime.now()
        feeder_1 = self._create_feeder(scheduled_arrival=now, service_name_suffix="1")
        feeder_1.large_scheduled_vehicle.capacity_in_teu = 20
        feeder_1.large_scheduled_vehicle.moved_capacity = 20
        feeder_1.large_scheduled_vehicle.save()
        feeder_2 = self._create_feeder(scheduled_arrival=now, service_name_suffix="2")
        feeder_2.large_scheduled_vehicle.capacity_in_teu = 20
        feeder_2.large_scheduled_vehicle.moved_capacity = 20
        feeder_2.large_scheduled_vehicle.save()

        self._create_container_delivered_by_large_scheduled_vehicle(feeder_1)

        self.report.generate()

        text = self.report.get_text_representation()
        self.assertEqual("""
Free Inbound Capacity Statistics
Minimum: 19.00
Maximum: 20.00
Mean:    19.50
Stddev:  0.71
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: 20.00
Maximum: 20.00
Mean:    20.00
Stddev:  0.00
(rounding errors might exist)
""", text)

    def test_two_loaded_ships_one_with_outbound_traffic(self):
        now = datetime.datetime.now()
        feeder_1 = self._create_feeder(scheduled_arrival=now, service_name_suffix="1")
        feeder_1.large_scheduled_vehicle.capacity_in_teu = 20
        feeder_1.large_scheduled_vehicle.moved_capacity = 20
        feeder_1.large_scheduled_vehicle.save()
        feeder_2 = self._create_feeder(scheduled_arrival=now, service_name_suffix="2")
        feeder_2.large_scheduled_vehicle.capacity_in_teu = 20
        feeder_2.large_scheduled_vehicle.moved_capacity = 20
        feeder_2.large_scheduled_vehicle.save()
        truck = self._create_truck(arrival=now)

        container = self._create_container_delivered_by_truck(truck)
        container.picked_up_by_large_scheduled_vehicle = feeder_1.id  # pylint: disable=no-member
        container.picked_up_by = feeder_1.get_mode_of_transport()
        container.save()

        self.report.generate()

        text = self.report.get_text_representation()
        self.assertEqual("""
Free Inbound Capacity Statistics
Minimum: 20.00
Maximum: 20.00
Mean:    20.00
Stddev:  0.00
(rounding errors might exist)

Free Outbound Capacity Statistics
Minimum: 19.00
Maximum: 20.00
Mean:    19.50
Stddev:  0.71
(rounding errors might exist)
""", text)
