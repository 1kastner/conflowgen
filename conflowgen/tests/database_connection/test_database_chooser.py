import unittest
from unittest.mock import MagicMock

from conflowgen.api.database_chooser import (
    DatabaseChooser,
    NoCurrentConnectionException,
)


class TestDatabaseChooser(unittest.TestCase):
    def setUp(self):
        self.chooser = DatabaseChooser()

    def test_close_without_open(self):
        """If there isn't an open db, raise Exception."""
        with self.assertRaises(NoCurrentConnectionException):
            self.chooser.close_current_connection()

    def test_close_with_open_connection_calls_close(self):
        """If there is an open db, close it."""
        mock_db = MagicMock()
        self.chooser.peewee_sqlite_db = mock_db
        self.chooser.close_current_connection()
        mock_db.close.assert_called_once()
        self.assertIsNone(self.chooser.peewee_sqlite_db)

    def test_existing_database_connection(self):
        """Loading an existing db with no previous open."""
        self.chooser.sqlite_database_connection = MagicMock()
        mock_db = MagicMock()
        self.chooser.sqlite_database_connection.choose_database.return_value = mock_db
        self.chooser.load_existing_sqlite_database("test.sqlite")
        self.chooser.sqlite_database_connection.choose_database.assert_called_once_with(
            "test.sqlite", create=False, reset=False
        )
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db)

    def test_existing_database_connection_close_previous(self):
        """
        Loading an existing db with one open already should
        close the previous.
        """
        self.chooser.sqlite_database_connection = MagicMock()
        mock_db_1 = MagicMock()
        mock_db_2 = MagicMock()

        self.chooser.sqlite_database_connection.choose_database.side_effect = [
            mock_db_1,
            mock_db_2,
        ]

        self.chooser.load_existing_sqlite_database("db1.sqlite")
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db_1)

        self.chooser.load_existing_sqlite_database("db2.sqlite")

        mock_db_1.close.assert_called_once()
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db_2)

    def test_create_new_sqlite_database_open(self):
        """
        Creating a new db with one open already should
        close the previous.
        """
        self.chooser._close_and_reset_db = MagicMock()  # pylint: disable=protected-access
        self.chooser.sqlite_database_connection = MagicMock()
        mock_db = MagicMock()
        self.chooser.sqlite_database_connection.choose_database.return_value = mock_db

        self.chooser.peewee_sqlite_db = MagicMock()

        self.chooser.create_new_sqlite_database("db.sqlite", overwrite=False)

        self.chooser._close_and_reset_db.assert_called_once()  # pylint: disable=protected-access

        self.chooser.sqlite_database_connection.choose_database.assert_called_once_with(
            "db.sqlite", create=True, reset=False
        )
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db)

    def test_create_new_sqlite_database(self):
        """Creating a new db without one open already."""
        self.chooser._close_and_reset_db = MagicMock()  # pylint: disable=protected-access
        self.chooser.sqlite_database_connection = MagicMock()
        mock_db = MagicMock()
        self.chooser.sqlite_database_connection.choose_database.return_value = mock_db

        self.chooser.peewee_sqlite_db = None

        self.chooser.create_new_sqlite_database("db.sqlite", overwrite=False)

        self.chooser._close_and_reset_db.assert_not_called()  # pylint: disable=protected-access
        self.chooser.sqlite_database_connection.choose_database.assert_called_once_with(
            "db.sqlite", create=True, reset=False
        )
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db)

    def test_list_all_sqlite_database(self):
        """Test listing all db function."""
        self.chooser.sqlite_database_connection = MagicMock()
        self.chooser.sqlite_database_connection.list_all_sqlite_databases.return_value = [
            "db.sqlite"
        ]
        self.assertEqual(self.chooser.list_all_sqlite_databases(), ["db.sqlite"])
