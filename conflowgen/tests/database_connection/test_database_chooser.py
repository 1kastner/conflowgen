
import unittest
from unittest.mock import MagicMock
import conflowgen
from conflowgen.api.database_chooser import DatabaseChooser, NoCurrentConnectionException

class TestDatabaseChooser(unittest.TestCase):
    def setUp(self):
        self.chooser = DatabaseChooser()
    
    # If there isn't an open db, raise Exception.

    def test_close_without_open(self):
        with self.assertRaises(NoCurrentConnectionException):
            self.chooser.close_current_connection()

    # If there is an open db close it.

    def test_close_with_open_connection_calls_close(self):
        mock_db = MagicMock()
        self.chooser.peewee_sqlite_db = mock_db
        self.chooser.close_current_connection()
        mock_db.close.assert_called_once()
        self.assertIsNone(self.chooser.peewee_sqlite_db)

    # Loading an existing db with no previous open.

    def test_existing_database_connection(self):
        self.chooser.sqlite_database_connection = MagicMock()
        mock_db = MagicMock()
        self.chooser.sqlite_database_connection.choose_database.return_value = mock_db
        self.chooser.load_existing_sqlite_database("test.sqlite")
        self.chooser.sqlite_database_connection.choose_database.assert_called_once_with(
            "test.sqlite", create=False, reset=False
        )
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db)

    # Loading an exisiting db with one open already, close the previous.

    def test_existing_database_connection_close_previous(self):

        self.chooser.sqlite_database_connection = MagicMock()
        mock_db_1 = MagicMock()
        mock_db_2 = MagicMock()

        self.chooser.sqlite_database_connection.choose_database.side_effect = [mock_db_1, mock_db_2]

        self.chooser.load_existing_sqlite_database("db1.sqlite")
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db_1)

        self.chooser.load_existing_sqlite_database("db2.sqlite")

        mock_db_1.close.assert_called_once()              
        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db_2) 
    
    
    # Creating an exisiting db with one open already, close the previous.

    def test_create_new_sqlite_database_open(self):
        self.chooser._close_and_reset_db = MagicMock()
        self.chooser.sqlite_database_connection = MagicMock()
        mock_db = MagicMock()
        self.chooser.sqlite_database_connection.choose_database.return_value = mock_db
    
        self.chooser.peewee_sqlite_db = MagicMock()

        self.chooser.create_new_sqlite_database("db.sqlite", overwrite = False)
        self.chooser._close_and_reset_db.assert_called_once()

        self.chooser.sqlite_database_connection.choose_database.assert_called_once_with(
            "db.sqlite", create=True, reset=False
        )

        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db)

    # Creating an exisiting db without one open already.

    def test_create_new_sqlite_database(self):
        self.chooser._close_and_reset_db = MagicMock()
        self.chooser.sqlite_database_connection = MagicMock()
        mock_db = MagicMock()
        self.chooser.sqlite_database_connection.choose_database.return_value = mock_db
    
        self.chooser.peewee_sqlite_db = None

        self.chooser.create_new_sqlite_database("db.sqlite", overwrite = False)
        self.chooser._close_and_reset_db.assert_not_called()
        self.chooser.sqlite_database_connection.choose_database.assert_called_once_with(
            "db.sqlite", create=True, reset=False
        )

        self.assertEqual(self.chooser.peewee_sqlite_db, mock_db)
    
    # Test listing all db function.
    
    def test_list_all_sqlite_database(self):
        self.chooser.sqlite_database_connection = MagicMock()
        self.chooser.sqlite_database_connection.list_all_sqlite_databases.return_value = ["db.sqlite"]
        self.assertEqual(self.chooser.list_all_sqlite_databases(), ["db.sqlite"])

        

