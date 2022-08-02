import datetime
import unittest

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck
from conflowgen.application.services.export_container_flow_service import \
    ExportContainerFlowService
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestExportContainerFlowService__Container(unittest.TestCase):  # pylint: disable=invalid-name

    def setUp(self) -> None:
        self.service = ExportContainerFlowService()

    def test_convert_empty_table_to_pandas_dataframe(self):
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Container,
            Schedule,
            Destination
        ])
        df_container = self.service._convert_table_to_pandas_dataframe(Container)  # pylint: disable=protected-access
        self.assertEqual(len(df_container), 0)

    def test_convert_table_to_pandas_dataframe_with_container_without_destination(self):
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            Container,
            Truck,
            LargeScheduledVehicle,
            Destination
        ])
        container = Container.create(
            weight=20,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.feeder,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard
        )
        container.save()
        df_container = self.service._convert_table_to_pandas_dataframe(Container)  # pylint: disable=protected-access
        self.assertEqual(len(df_container), 1)
        self.assertSetEqual(
            set(df_container.columns),
            {
                "weight", "delivered_by", "picked_up_by", "length", "storage_requirement",
                "picked_up_by_truck", "picked_up_by_vehicle", "delivered_by_truck",
                "delivered_by_vehicle", "emergency_pickup", "picked_up_by_initial"
            }
        )
        self.assertEqual(
            df_container.index.name,
            "id"
        )
        container_df_entry = df_container.iloc[0]
        self.assertEqual(
            container_df_entry.weight,
            20
        )
        self.assertEqual(
            container_df_entry.delivered_by,
            "truck"
        )
        self.assertEqual(
            container_df_entry.picked_up_by,
            "deep_sea_vessel"
        )
        self.assertEqual(
            container_df_entry.length,
            20
        )
        self.assertEqual(
            container_df_entry.storage_requirement,
            "standard"
        )
        self.assertEqual(
            container_df_entry.picked_up_by_truck,
            None
        )
        self.assertEqual(
            container_df_entry.picked_up_by_vehicle,
            None
        )
        self.assertEqual(
            container_df_entry.delivered_by_truck,
            None
        )
        self.assertEqual(
            container_df_entry.delivered_by_vehicle,
            None
        )

    def test_convert_table_to_pandas_dataframe_with_container_with_destination(self):
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Container,
            Schedule,
            Truck,
            LargeScheduledVehicle,
            Destination
        ])
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        destination = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=1,
            destination_name="TestDestination1",
            fraction=0.4
        )
        Container.create(
            weight=20,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.feeder,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            destination=destination
        )
        df_container = self.service._convert_table_to_pandas_dataframe(Container)   # pylint: disable=protected-access
        self.assertEqual(len(df_container), 1)
        self.assertSetEqual(
            set(df_container.columns),
            {
                "weight", "delivered_by", "picked_up_by", "length", "storage_requirement",
                "picked_up_by_truck", "picked_up_by_vehicle", "delivered_by_truck",
                "delivered_by_vehicle", "emergency_pickup", "picked_up_by_initial",
                "destination_name", "destination_sequence_id"
            }
        )
        self.assertEqual(
            df_container.index.name,
            "id"
        )
        container_df_entry = df_container.iloc[0]
        self.assertEqual(
            container_df_entry.weight,
            20
        )
        self.assertEqual(
            container_df_entry.delivered_by,
            "truck"
        )
        self.assertEqual(
            container_df_entry.picked_up_by,
            "deep_sea_vessel"
        )
        self.assertEqual(
            container_df_entry.length,
            20
        )
        self.assertEqual(
            container_df_entry.storage_requirement,
            "standard"
        )
        self.assertEqual(
            container_df_entry.picked_up_by_truck,
            None
        )
        self.assertEqual(
            container_df_entry.picked_up_by_vehicle,
            None
        )
        self.assertEqual(
            container_df_entry.delivered_by_truck,
            None
        )
        self.assertEqual(
            container_df_entry.delivered_by_vehicle,
            None
        )
        self.assertEqual(
            container_df_entry.destination_name,
            "TestDestination1"
        )
        self.assertEqual(
            container_df_entry.destination_sequence_id,
            1
        )
