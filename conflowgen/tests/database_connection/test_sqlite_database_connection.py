import unittest
from unittest.mock import patch, MagicMock
import os

from conflowgen.database_connection.sqlite_database_connection import (
    SqliteDatabaseConnection,
    SqliteDatabaseIsMissingException,
    SqliteDatabaseAlreadyExistsException,
)


class TestSqliteDatabaseConnection(unittest.TestCase):
    def setUp(self):
        self.conn = SqliteDatabaseConnection(sqlite_databases_directory="/fake/path")

    @patch("conflowgen.database_connection.sqlite_database_connection.SqliteDatabase")
    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isfile", return_value=False)
    def test_choose_database_creates_new(self, _mock_isfile, mock_sqlite_db):
        """Ensure that creating a new database works as expected."""
        mock_db = MagicMock()
        mock_sqlite_db.return_value = mock_db

        with patch(
            "conflowgen.database_connection.sqlite_database_connection.create_tables"
        ) as mock_create, patch(
            "conflowgen.database_connection.sqlite_database_connection.seed_all_distributions"
        ) as mock_seed, patch(
            "conflowgen.database_connection.sqlite_database_connection.get_initialised_random_object",
            return_value=MagicMock()
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.ContainerFlowGenerationProperties.get_or_none",
            return_value=None
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Container.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Truck.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Train.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Barge.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Feeder.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.DeepSeaVessel.select"
        ):
            db = self.conn.choose_database("test.sqlite", create=True)

        mock_sqlite_db.assert_called_once()
        mock_db.connect.assert_called_once()
        mock_create.assert_called_once()
        mock_seed.assert_called_once()
        self.assertEqual(db, mock_db)

    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isfile", return_value=True)
    def test_choose_database_raises_if_exists_and_create(self, _mock_isfile):
        """Trying to create a database that already exists raises an Exception."""
        self.assertRaises(
            SqliteDatabaseAlreadyExistsException,
            self.conn.choose_database,
            "exists.sqlite",
            create=True,
            reset=False
        )

    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isfile", return_value=False)
    def test_choose_database_raises_if_missing_and_not_create(self, _mock_isfile):
        """Opening a non existent database raises an Exception."""
        self.assertRaises(
            SqliteDatabaseIsMissingException,
            self.conn.choose_database,
            "missing.sqlite",
            create=False
        )

    @patch("conflowgen.database_connection.sqlite_database_connection.SqliteDatabase")
    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isfile", return_value=True)
    def test_choose_database_resets_existing(self, _mock_isfile, mock_sqlite_db):
        """Ensure that resetting an existing database works as expected."""
        mock_db = MagicMock()
        mock_sqlite_db.return_value = mock_db

        with patch(
            "conflowgen.database_connection.sqlite_database_connection.os.remove"
        ) as mock_remove, patch(
            "conflowgen.database_connection.sqlite_database_connection.create_tables"
        ) as mock_create, patch(
            "conflowgen.database_connection.sqlite_database_connection.seed_all_distributions"
        ) as mock_seed, patch(
            "conflowgen.database_connection.sqlite_database_connection.get_initialised_random_object",
            return_value=MagicMock()
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.ContainerFlowGenerationProperties.get_or_none",
            return_value=None
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Container.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Truck.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Train.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Barge.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Feeder.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.DeepSeaVessel.select"
        ):
            self.conn.choose_database("reset.sqlite", create=True, reset=True)

        mock_remove.assert_called_once()
        mock_create.assert_called_once()
        mock_seed.assert_called_once()

    @patch("conflowgen.database_connection.sqlite_database_connection.SqliteDatabase")
    def test_choose_database_in_memory(self, mock_sqlite_db):
        """Ensures opening an in-memory database works as intended."""
        mock_db = MagicMock()
        mock_sqlite_db.return_value = mock_db

        with patch(
            "conflowgen.database_connection.sqlite_database_connection.create_tables"
        ) as mock_create, patch(
            "conflowgen.database_connection.sqlite_database_connection.seed_all_distributions"
        ) as mock_seed, patch(
            "conflowgen.database_connection.sqlite_database_connection.get_initialised_random_object",
            return_value=MagicMock()
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.ContainerFlowGenerationProperties.get_or_none",
            return_value=None
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Container.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Truck.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Train.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Barge.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Feeder.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.DeepSeaVessel.select"
        ):
            db = self.conn.choose_database(":memory:", create=True)

        mock_sqlite_db.assert_called_once()
        mock_db.connect.assert_called_once()
        mock_create.assert_called_once()
        mock_seed.assert_called_once()
        self.assertEqual(db, mock_db)

    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isfile", return_value=True)
    @patch("conflowgen.database_connection.sqlite_database_connection.os.remove")
    def test_delete_existing_database(self, mock_remove, _mock_isfile):
        """Ensures that deleting a database works as intended."""
        self.conn.delete_database("delete.sqlite")
        mock_remove.assert_called_once()

    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isfile", return_value=False)
    def test_delete_missing_database(self, _mock_isfile):
        """Deleting a non-existing database raises an Exception."""
        self.assertRaises(
            SqliteDatabaseIsMissingException,
            self.conn.delete_database,
            "notfound.sqlite"
        )

    @patch("conflowgen.database_connection.sqlite_database_connection.os.listdir")
    def test_list_all_sqlite_databases_filters_only_sqlite(self, mock_listdir):
        """Ensures only .sqlite files are listed."""
        mock_listdir.return_value = ["a.sqlite", "b.txt", "c.sqlite"]
        result = self.conn.list_all_sqlite_databases()
        self.assertEqual(result, ["a.sqlite", "c.sqlite"])

    def test_sqlite_databases_directory_is_none(self):
        """Covers line 60"""
        conn = SqliteDatabaseConnection(sqlite_databases_directory=None)
        assert conn.sqlite_databases_directory.endswith("data\\databases")

    @patch("conflowgen.database_connection.sqlite_database_connection.os.makedirs")
    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isdir", return_value=False)
    def test_sqlite_databases_directory_is_not_dir(self, mock_isdir, mock_makedirs):
        """Covers lines 68-69"""
        conn = SqliteDatabaseConnection(sqlite_databases_directory="not_a_directory")
        self.assertEqual(conn.sqlite_databases_directory, os.path.abspath("not_a_directory"))
        mock_isdir.assert_called_once_with(conn.sqlite_databases_directory)
        mock_makedirs.assert_called_once_with(conn.sqlite_databases_directory, exist_ok=True)

    @patch("conflowgen.database_connection.sqlite_database_connection.SqliteDatabase")
    @patch("conflowgen.database_connection.sqlite_database_connection.os.path.isfile", return_value=True)
    def test_choose_database_opens_existing_without_reset(self, _mock_isfile, mock_sqlite_db):
        """Covers missing line 114"""
        mock_db = MagicMock()
        mock_sqlite_db.return_value = mock_db

        with patch(
            "conflowgen.database_connection.sqlite_database_connection.create_tables"
        ) as mock_create, patch(
            "conflowgen.database_connection.sqlite_database_connection.seed_all_distributions"
        ) as mock_seed, patch(
            "conflowgen.database_connection.sqlite_database_connection.get_initialised_random_object",
            return_value=MagicMock()
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.ContainerFlowGenerationProperties.get_or_none",
            return_value=None
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Container.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Truck.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Train.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Barge.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.Feeder.select"
        ), patch(
            "conflowgen.database_connection.sqlite_database_connection.DeepSeaVessel.select"
        ):
            self.conn.choose_database("existing.sqlite", create=False, reset=False)

        mock_create.assert_not_called()
        mock_seed.assert_not_called()

    @patch("conflowgen.database_connection.sqlite_database_connection.SqliteDatabase")
    @patch("conflowgen.database_connection.sqlite_database_connection.ContainerFlowGenerationProperties.get_or_none")
    def test_choose_database_logs_container_flow_properties(self, mock_get_or_none, mock_sqlite_db):
        """Covers missing lines 119-124"""
        mock_db = MagicMock()
        mock_sqlite_db.return_value = mock_db

        fake_props = MagicMock()
        fake_props.name = "Test"
        fake_props.start_date = "Test"
        fake_props.end_date = "Test"
        fake_props.generated_at = "Test"
        fake_props.last_updated_at = "Test"
        fake_props.transportation_buffer = 0
        mock_get_or_none.return_value = fake_props

        with patch("conflowgen.database_connection.sqlite_database_connection.create_tables"), \
             patch("conflowgen.database_connection.sqlite_database_connection.seed_all_distributions"), \
             patch("conflowgen.database_connection.sqlite_database_connection.get_initialised_random_object",
                   return_value=MagicMock()), \
             patch("conflowgen.database_connection.sqlite_database_connection.Container.select"), \
             patch("conflowgen.database_connection.sqlite_database_connection.Truck.select"), \
             patch("conflowgen.database_connection.sqlite_database_connection.Train.select"), \
             patch("conflowgen.database_connection.sqlite_database_connection.Barge.select"), \
             patch("conflowgen.database_connection.sqlite_database_connection.Feeder.select"), \
             patch("conflowgen.database_connection.sqlite_database_connection.DeepSeaVessel.select"):
            self.conn.choose_database(":memory:", create=True)

        mock_sqlite_db.assert_called_once()
        mock_get_or_none.assert_called_once()
