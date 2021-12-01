import unittest

from conflowgen.database_connection.sqlite_database_connection import SqliteDatabaseConnection, \
    SqliteDatabaseIsMissingException


class TestSqliteDatabaseConnection(unittest.TestCase):

    def setUp(self) -> None:
        self.sqlite_database_connection = SqliteDatabaseConnection()
        databases = self.sqlite_database_connection.list_all_sqlite_databases()
        self.assertNotIn("not-existent.sqlite", databases)

    def test_list_all_sqlite_databases(self):
        databases = self.sqlite_database_connection.list_all_sqlite_databases()
        self.assertNotIn(".gitkeep", databases)
        for database_file_name in databases:
            self.assertIn(".sqlite", database_file_name)

    def test_reject_creation_if_create_is_false(self):
        with self.assertRaises(SqliteDatabaseIsMissingException):
            self.sqlite_database_connection.choose_database(
                "not-existent.sqlite",
                create=False,
                reset=True
            )
        with self.assertRaises(SqliteDatabaseIsMissingException):
            self.sqlite_database_connection.choose_database(
                "not-existent.sqlite",
                create=False,
                reset=False
            )

    def test_load_existent_database_without_reset(self):
        test_database_name = "testing-existent--test_load_existent_database_without_reset.sqlite"
        if test_database_name in self.sqlite_database_connection.list_all_sqlite_databases():
            self.sqlite_database_connection.delete_database(test_database_name)
        sqlite_db_connection_1 = self.sqlite_database_connection.choose_database(
            test_database_name,
            create=True,
            reset=False
        )
        successfully_closed_1 = sqlite_db_connection_1.close()
        self.assertTrue(successfully_closed_1)
        sqlite_db_connection_2 = self.sqlite_database_connection.choose_database(
            test_database_name,
            create=False,
            reset=False
        )
        successfully_closed_2 = sqlite_db_connection_2.close()
        self.assertTrue(successfully_closed_2)
        self.sqlite_database_connection.delete_database(test_database_name)

    def test_load_existent_database_with_reset(self):
        test_database_name = "testing-existent--test_load_existent_database_with_reset.sqlite"
        if test_database_name in self.sqlite_database_connection.list_all_sqlite_databases():
            self.sqlite_database_connection.delete_database(test_database_name)
        sqlite_db_connection_1 = self.sqlite_database_connection.choose_database(
            test_database_name,
            create=True,
            reset=False
        )
        successfully_closed_1 = sqlite_db_connection_1.close()
        self.assertTrue(successfully_closed_1)
        sqlite_db_connection_2 = self.sqlite_database_connection.choose_database(
            test_database_name,
            create=False,
            reset=True
        )
        successfully_closed_2 = sqlite_db_connection_2.close()
        self.assertTrue(successfully_closed_2)
        self.sqlite_database_connection.delete_database(test_database_name)
