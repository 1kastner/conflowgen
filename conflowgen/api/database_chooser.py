import logging
from typing import List, Optional

from peewee import SqliteDatabase

from conflowgen.database_connection.sqlite_database_connection import SqliteDatabaseConnection


class NoCurrentConnectionException(Exception):
    pass


class DatabaseChooser:
    """
    This is a stateful library. For the purpose of reproducibility, the current input distributions are all stored in
    the database, likewise the generated vehicles etc. Thus, different scenarios can be stored in different SQLite
    databases.
    """

    def __init__(self, sqlite_databases_directory: Optional[str] = None):
        """
        Args:
            sqlite_databases_directory: The DatabaseChooser opens one directory. All databases are saved to and load
                from this directory. It defaults to ``<project root>/data/databases/``.
        """
        self.logger = logging.getLogger("conflowgen")
        self.sqlite_database_connection = SqliteDatabaseConnection(
            sqlite_databases_directory=sqlite_databases_directory
        )
        self.peewee_sqlite_db: Optional[SqliteDatabase] = None

    def list_all_sqlite_databases(self) -> List[str]:
        """
        Returns:
             A list of all SQLite databases in the opened directory
        """
        all_sqlite_databases = self.sqlite_database_connection.list_all_sqlite_databases()
        return all_sqlite_databases

    def load_existing_sqlite_database(self, file_name: str) -> None:
        """
        Args:
            file_name: The file name of an SQLite database in the opened directory
        """
        if self.peewee_sqlite_db is not None:
            self._close_and_reset_db()
        self.peewee_sqlite_db = self.sqlite_database_connection.choose_database(file_name, create=False, reset=False)

    def create_new_sqlite_database(self, file_name: str, **seeder_options) -> None:
        """
        Args:
            file_name: The file name of an SQLite database that will reside in ``<project root>/data/databases/``
            **seeder_options: In case the database is seeded with default values, some variations exist that the user
                can choose from. The following options exist:

        For the seeder options, the following keywords are available:
            * ``assume_tas (bool)``: Whether to assume a truck appointment system for the truck arrival distribution.
              Based on this selection, one of the two truck arrival distributions is chosen.

        All required tables are created and all input distributions are seeded with default values. These can be simply
        overwritten by the use-case specific distributions with the help of the API, e.g. the
        :class:`.ContainerLengthDistributionManager`,
        :class:`.ContainerStorageRequirementDistributionManager`,
        :class:`.ModeOfTransportDistributionManager`,
        :class:`.TruckArrivalDistributionManager`,
        or similar.
        By default, no schedules and no vehicles exist.
        """
        if self.peewee_sqlite_db is not None:
            self._close_and_reset_db()
        self.peewee_sqlite_db = self.sqlite_database_connection.choose_database(
            file_name, create=True, reset=False, **seeder_options)

    def close_current_connection(self) -> None:
        """
        Close current connection, e.g. as a preparatory step to create a new SQLite database.
        """
        if self.peewee_sqlite_db:
            self._close_and_reset_db()
        else:
            raise NoCurrentConnectionException("You must first create a connection to an SQLite database.")

    def _close_and_reset_db(self):
        self.logger.debug("Closing current database connection.")
        self.peewee_sqlite_db.close()
        self.peewee_sqlite_db = None
