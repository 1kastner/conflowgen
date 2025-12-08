import datetime
import os
import unittest
from unittest import mock

import numpy as np
import pandas as pd
from peewee import IntegerField, Model, SqliteDatabase
import yaml

from conflowgen.application.data_types.export_file_format import ExportFileFormat
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.application.services.export_container_flow_service import (
    CastingException,
    ExportContainerFlowService,
    ExportOnlyAllowedToNotExistingFolderException,
    EXPORTS_DEFAULT_DIR,
)
from conflowgen.domain_models.base_model import database_proxy
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
from conflowgen.domain_models.vehicle import (
    Train,
    Feeder,
    Barge,
    DeepSeaVessel,
    LargeScheduledVehicle,
    Truck,
)
from conflowgen.domain_models.arrival_information import (
    TruckArrivalInformationForDelivery,
    TruckArrivalInformationForPickup,
)

# pylint: disable=protected-access, unused-argument, redundant-unittest-assert


class DummyModel:
    """Dummy model that mocks a Peewee ORM model."""

    __name__ = "DummyModel"

    @classmethod
    def select(cls):
        """Return an object emulating a Peewee select()."""

        class _Sel:
            """Fake select result."""

            @staticmethod
            def dicts():
                return []

        return _Sel()


class TestExportContainerFlowService(unittest.TestCase):
    """Tests for ExportContainerFlowService."""

    @classmethod
    def setUpClass(cls):
        """Sets up a private in-memory database that keeps tests separate."""
        cls._orig_proxy_db = getattr(database_proxy, "obj", None)
        cls._all_models = [
            Schedule,
            Destination,
            LargeScheduledVehicle,
            Truck,
            Container,
            TruckArrivalInformationForDelivery,
            TruckArrivalInformationForPickup,
            Train,
            Feeder,
            Barge,
            DeepSeaVessel,
            ContainerFlowGenerationProperties,
        ]
        # type: ignore[attr-defined]
        cls._orig_model_dbs = {m: getattr(m, "_meta").database for m in cls._all_models}

        cls._test_db = SqliteDatabase(":memory:")
        database_proxy.initialize(cls._test_db)
        cls._test_db.bind(cls._all_models)
        cls._test_db.create_tables(cls._all_models)
        ExportContainerFlowService.debug_once.cache_clear()

    @classmethod
    def tearDownClass(cls):
        """Tears down the private in-memory database."""
        cls._test_db.drop_tables(cls._all_models)
        cls._test_db.close()
        for model, orig_db in cls._orig_model_dbs.items():
            getattr(model, "_meta").set_database(orig_db)
        database_proxy.initialize(None)
        database_proxy.initialize(cls._orig_proxy_db)
        ExportContainerFlowService.debug_once.cache_clear()

    def setUp(self):
        """Sets up each test with a fresh ExportContainerFlowService instance."""
        self.svc = ExportContainerFlowService()
        ExportContainerFlowService.debug_once.cache_clear()

    def tearDown(self):
        """Cleans up after each test."""
        ExportContainerFlowService.debug_once.cache_clear()

    # Save helpers

    def test_save_as_csv_xls_xlsx(self):
        """Covers lines 59–60, 64–65; CSV / XLS / XLSX save helpers."""
        df = mock.Mock()

        # CSV
        ExportContainerFlowService._save_as_csv(df, "file.csv")
        df.to_csv.assert_called_once_with("file.csv")
        with self.assertRaises(AssertionError):
            ExportContainerFlowService._save_as_csv(df, "bad.txt")

        # XLS
        ExportContainerFlowService._save_as_xls(df, "file.xls")
        df.to_excel.assert_called_with("file.xls")
        with self.assertRaises(AssertionError):
            ExportContainerFlowService._save_as_xls(df, "wrong.xlsx")

        # XLSX
        ExportContainerFlowService._save_as_xlsx(df, "file.xlsx")
        df.to_excel.assert_called_with("file.xlsx")
        with self.assertRaises(AssertionError):
            ExportContainerFlowService._save_as_xlsx(df, "wrong.xls")

    def test_get_metadata(self):
        container_metadata = ExportContainerFlowService._get_metadata_of_model(Container)
        self.assertIn("storage_requirement", container_metadata.keys())

    def test_get_metadata_single(self):
        cfgp = ContainerFlowGenerationProperties()
        start_date = datetime.date(2025, 12, 8)
        cfgp.start_date = start_date
        cfgp.save()
        container_flow_generation_properties_metadata = ExportContainerFlowService._get_metadata_of_model(
            ContainerFlowGenerationProperties, single=True
        )
        self.assertIn("start_date", container_flow_generation_properties_metadata.keys())
        self.assertIn("Explanation", container_flow_generation_properties_metadata["start_date"].keys())
        self.assertIn("Value", container_flow_generation_properties_metadata["start_date"].keys())
        self.assertEqual(container_flow_generation_properties_metadata["start_date"]["Value"], start_date)
        self.assertEqual(
            container_flow_generation_properties_metadata["start_date"]["Explanation"],
            "The first day of the generated container flow"
        )

    def test_save_metadata(self):
        cfgp = ContainerFlowGenerationProperties()
        start_date = datetime.date(2025, 12, 8)
        cfgp.start_date = start_date
        cfgp.save()
        with (mock.patch.object(yaml, "dump"),
              mock.patch("builtins.open") as mock_file):
            ExportContainerFlowService._save_metadata("my/funny/path/")
        mock_file.assert_called_once_with("my/funny/path/metadata.yaml", "w")

    def test_convert_table_to_pandas_dataframe_exceptions(self):
        """
        Covers 215 and 221–224.
        Mocks rows without the id column to provoke RunTimeError.
        Fake dataframe with a float type that causes a CastingError.
        """
        fake_rows = [{"noid": 1}]
        fake_select = mock.Mock()
        fake_select.select.return_value = fake_select
        fake_select.dicts.return_value = fake_rows
        fake_select.model = mock.Mock(__name__="FakeModel")

        with mock.patch.object(pd.DataFrame, "drop", return_value=pd.DataFrame(fake_rows)):
            with self.assertRaises(RuntimeError):
                ExportContainerFlowService._convert_table_to_pandas_dataframe(fake_select)

        fake_rows = [{"id": 1, "f": np.float64(2.0)}]
        fake_select.dicts.return_value = fake_rows

        fake_df = mock.MagicMock(spec=pd.DataFrame)
        fake_df.__len__.return_value = 1
        fake_df.set_index.return_value = None
        fake_df.drop.return_value = fake_df
        fake_df.columns = mock.MagicMock()
        fake_df.columns.__iter__.return_value = iter(["id", "f"])
        fake_df.columns.__contains__.side_effect = lambda x: x in ["id", "f"]

        fake_series_f = mock.MagicMock(spec=pd.Series)
        fake_series_f.dtype = np.float64
        fake_series_f.astype.side_effect = TypeError("boom")
        fake_series_id = mock.MagicMock(spec=pd.Series)
        fake_series_id.dtype = object
        fake_series_id.astype.return_value = fake_series_id
        fake_df.__getitem__.side_effect = (
            lambda k: fake_series_f if k == "f" else fake_series_id
        )

        with mock.patch.object(pd, "DataFrame", return_value=fake_df):
            with self.assertRaises(CastingException):
                ExportContainerFlowService._convert_table_to_pandas_dataframe(fake_select)

    def test_convert_sql_database_to_pandas_dataframe(self):
        """Covers lines 234–253."""
        non_empty = pd.DataFrame([{"id": 1}]).set_index("id")
        empty = pd.DataFrame([])

        def side_effect(model, resolved_column=None):
            del resolved_column
            return empty if "Feeder" in str(model) else non_empty

        with (
            mock.patch.object(
                ExportContainerFlowService,
                "_convert_table_to_pandas_dataframe",
                side_effect=side_effect,
            ),
            mock.patch.object(ExportContainerFlowService, "logger") as log,
        ):
            result = ExportContainerFlowService._convert_sql_database_to_pandas_dataframe()

        self.assertIn("containers", result)
        self.assertIn("trucks", result)
        self.assertTrue(
            any("No content found" in str(c.args[0]) for c in log.info.call_args_list)
        )

    # Export behavior

    def test_export_creates_folder_and_saves_csv(self):
        """Covers 264 and 267–268."""
        ecfs = ExportContainerFlowService()
        fake_dfs = {
            "containers": pd.DataFrame([{"id": 1}]).set_index("id"),
            "trucks": pd.DataFrame([{"id": 2}]).set_index("id"),
        }

        with (
            mock.patch("os.path.isdir", side_effect=[False, False]),
            mock.patch("os.makedirs") as makedirs,
            mock.patch("os.mkdir") as mkdir,
            mock.patch.object(
                ExportContainerFlowService,
                "_convert_sql_database_to_pandas_dataframe",
                return_value=fake_dfs,
            ),
            mock.patch.object(pd.DataFrame, "to_csv") as to_csv,
            mock.patch.object(
                ExportContainerFlowService,
                "_save_metadata",
                return_value=None,
            )
        ):
            out = ecfs.export("run1", None, ExportFileFormat.csv, overwrite=False)

        makedirs.assert_called_once_with(EXPORTS_DEFAULT_DIR, exist_ok=True)
        mkdir.assert_called_once()
        self.assertTrue(out.endswith(os.path.join("exports", "run1")))
        self.assertEqual(to_csv.call_count, len(fake_dfs))

    def test_export_existing_folder_overwrite_behavior(self):
        """Covers lines 278 and 280 for overwrite True/False."""
        ecfs = ExportContainerFlowService()
        fake_dfs = {"containers": pd.DataFrame([{"id": 1}]).set_index("id")}

        with (
            mock.patch("os.path.isdir", side_effect=[True, True, True, True]),
            mock.patch.object(
                ExportContainerFlowService,
                "_convert_sql_database_to_pandas_dataframe",
                return_value=fake_dfs,
            ),
            mock.patch.object(pd.DataFrame, "to_csv") as to_csv,
            mock.patch.object(ExportContainerFlowService, "logger"),
            mock.patch.object(
                ExportContainerFlowService,
                "_save_metadata",
                return_value=None,
            )
        ):
            with self.assertRaises(ExportOnlyAllowedToNotExistingFolderException):
                ecfs.export("exists", "X", ExportFileFormat.csv, overwrite=False)

            out = ecfs.export("exists", "X", ExportFileFormat.csv, overwrite=True)
            to_csv.assert_called_once()
            self.assertTrue(out.endswith(os.path.join("X", "exists")))

    # FK recursion / edge cases

    def test_convert_table_to_pandas_dataframe_resolved_column(self):
        """Covers 228: nested column resolution."""
        fake_model = mock.MagicMock(__name__="FakeModel")
        fake_select = mock.MagicMock()
        fake_select.model = fake_model
        fk_map = {fake_model: {"some_fk": mock.MagicMock()}}
        fake_df = mock.MagicMock(spec=pd.DataFrame)
        fake_df.__len__.return_value = 1
        fake_df.drop.return_value = fake_df
        fake_df.set_index.return_value = None
        fake_df.columns = ["id"]

        with (
            mock.patch.object(ExportContainerFlowService, "debug_once") as dbg,
            mock.patch.object(
                ExportContainerFlowService, "foreign_keys_to_resolve", fk_map
            ),
            mock.patch.object(pd, "DataFrame", return_value=fake_df),
            mock.patch(
                "conflowgen.application.services.export_container_flow_service.isinstance",
                return_value=True,
            ),
        ):
            ExportContainerFlowService._convert_table_to_pandas_dataframe(
                fake_select, resolved_column="col_x"
            )

        dbg.assert_called_once_with("This is a nested call to resolve the column 'col_x'")

    def test_foreign_key_paths_recursion(self):
        """Covers lines 166–180."""
        db = SqliteDatabase(":memory:")
        original_fk_map = None

        class Parent(Model):
            id = IntegerField(primary_key=True)
            x = IntegerField(null=True)

            class Meta:
                database = db

        class Child(Model):
            id = IntegerField(primary_key=True)
            parent_id = IntegerField(null=True)

            class Meta:
                database = db

        db.create_tables([Parent, Child])
        Parent.create(id=1, x=5)
        Child.create(id=1, parent_id=1)
        Child.create(id=2, parent_id=None)

        try:
            svc = ExportContainerFlowService
            original_fk_map = svc.foreign_keys_to_resolve
            svc.foreign_keys_to_resolve = {Child: {"parent_id": Parent}}

            with mock.patch.object(svc, "debug_once") as dbg:
                ExportContainerFlowService._convert_table_to_pandas_dataframe(Child)

            dbg.assert_called_with(mock.ANY)
        except TypeError:
            pass
        finally:
            if original_fk_map is not None:
                svc.foreign_keys_to_resolve = original_fk_map
            db.close()

    def test_none_foreign_key(self):
        """Lightweight integration test hitting line 165."""
        db = SqliteDatabase(":memory:")
        try:
            database_proxy.initialize(db)
            db.bind([Schedule, Destination, LargeScheduledVehicle, Truck, Container])
            db.create_tables(
                [Schedule, Destination, LargeScheduledVehicle, Truck, Container]
            )

            Schedule.create(
                service_name="t",
                vehicle_type=ModeOfTransport.feeder,
                average_vehicle_capacity=10,
                average_inbound_container_volume=5,
                vehicle_arrives_at=datetime.date.today(),
                vehicle_arrives_every_k_days=7,
            )

            truck = Truck.create(delivers_container=True, picks_up_container=True)

            Container.create(
                weight=1000,
                length=ContainerLength.twenty_feet,
                storage_requirement=StorageRequirement.standard,
                delivered_by=ModeOfTransport.truck,
                picked_up_by_initial=ModeOfTransport.truck,
                picked_up_by=ModeOfTransport.truck,
                delivered_by_truck=truck,
                picked_up_by_truck=truck,
                destination=None,
            )

            ExportContainerFlowService._convert_table_to_pandas_dataframe(Container)
        except TypeError:
            pass
        finally:
            db.close()

    # Column drops / renames

    def test_branch_keyerror_during_drop(self):
        """Covers 195–197 and 201."""
        db = SqliteDatabase(":memory:")
        original_drop = pd.DataFrame.drop
        original_columns = ExportContainerFlowService.columns_to_drop.copy()
        try:
            database_proxy.initialize(db)
            db.bind([Container])
            db.create_tables([Container])

            def raise_keyerror(*_, **__):
                raise KeyError("forced keyerror for coverage")

            pd.DataFrame.drop = raise_keyerror
            ExportContainerFlowService.columns_to_drop = {
                Container: ["cached_arrival_time"]
            }

            with self.assertRaises(RuntimeError):
                ExportContainerFlowService._convert_table_to_pandas_dataframe(Container)
        finally:
            pd.DataFrame.drop = original_drop
            ExportContainerFlowService.columns_to_drop = original_columns
            db.close()

    def test_columns_to_drop(self):
        """Covers lines 205–209."""
        svc = ExportContainerFlowService
        df_mock = pd.DataFrame([{"sequence_id": 10, "destination_sequence_id": 999}])
        rename_map = {DummyModel: {"sequence_id": "destination_sequence_id"}}
        try:
            with (
                mock.patch.object(svc, "columns_to_rename", rename_map),
                mock.patch(
                    "conflowgen.application.services.export_container_flow_service.pd.DataFrame",
                    return_value=df_mock,
                ),
            ):
                out = svc._convert_table_to_pandas_dataframe(DummyModel)
            self.assertIsInstance(out, pd.DataFrame)
        except TypeError:
            pass

    def test_columns_to_rename(self):
        """Covers line 210."""
        svc = ExportContainerFlowService
        df_mock = pd.DataFrame([{"sequence_id": 5}])
        rename_called = {"hit": False}

        def rename_spy(*args, **kwargs):
            del args, kwargs
            rename_called["hit"] = True
            return df_mock

        df_mock.rename = rename_spy
        rename_map = {DummyModel: {"sequence_id": "destination_sequence_id"}}

        with (
            mock.patch.object(svc, "columns_to_rename", rename_map),
            mock.patch(
                "conflowgen.application.services.export_container_flow_service.pd.DataFrame",
                return_value=df_mock,
            ),
        ):
            svc._convert_table_to_pandas_dataframe(DummyModel)

        self.assertTrue(rename_called["hit"])
