import logging
import os
from typing import List, Tuple, Optional

from peewee import SqliteDatabase

from conflowgen.database_connection.create_tables import create_tables
from conflowgen.domain_models.base_model import database_proxy
from conflowgen.domain_models.distribution_seeders.seed_database import seed_all_distributions


class SqliteDatabaseIsMissingException(Exception):
    pass


class SqliteDatabaseAlreadyExistsException(Exception):
    pass


class AmbiguousParameterException(Exception):
    pass


class SqliteDatabaseConnection:
    """
    The SQLite database stores all content from the API calls to enable reproducible results.
    See :class:`.DatabaseChooser` for more information.
    """

    SQLITE_DEFAULT_SETTINGS = {
        # compare with recommended settings from
        # https://docs.peewee-orm.com/en/latest/peewee/database.html
        'journal_mode': 'wal',
        'cache_size': -32 * 1024,  # counted in KiB, thus this means 32 MB cache
        'foreign_keys': 1,
        'ignore_check_constraints': 0,
        'synchronous': 0
    }

    DEFAULT_SQLITE_ROOT_DIR = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        os.pardir,
        "data",
        "databases"
    )

    def __init__(self, sqlite_databases_directory: Optional[str] = None):
        self.logger = logging.getLogger("conflowgen")
        if sqlite_databases_directory is None:
            self.sqlite_databases_directory = self.DEFAULT_SQLITE_ROOT_DIR
            if not os.path.isdir(self.sqlite_databases_directory):
                self.logger.debug(f"Creating SQLite directory at '{sqlite_databases_directory}'")
                os.makedirs(self.sqlite_databases_directory, exist_ok=True)
        else:
            self.sqlite_databases_directory = sqlite_databases_directory
        self.sqlite_db_connection = None

    def list_all_sqlite_databases(self) -> List[str]:
        sqlite_databases = [_file for _file
                            in os.listdir(self.sqlite_databases_directory)
                            if _file.endswith("sqlite")]
        return sqlite_databases

    def choose_database(
            self,
            database_name: str,
            create: bool = False,
            reset: bool = False,
            **seeder_options
    ) -> SqliteDatabase:
        if database_name == ":memory:":
            path_to_sqlite_database = ":memory:"
            sqlite_database_existed_before = False
        else:
            path_to_sqlite_database, sqlite_database_existed_before = self._load_or_create_sqlite_file_on_hard_drive(
                database_name=database_name, create=create, reset=reset
            )

        self.logger.debug(f"Opening file '{path_to_sqlite_database}'")
        self.sqlite_db_connection = SqliteDatabase(
            path_to_sqlite_database,
            pragmas=self.SQLITE_DEFAULT_SETTINGS
        )
        database_proxy.initialize(self.sqlite_db_connection)
        self.sqlite_db_connection.connect()

        self.logger.debug(f'journal_mode: {self.sqlite_db_connection.journal_mode}')
        self.logger.debug(f'cache_size: {self.sqlite_db_connection.cache_size}')
        self.logger.debug(f'page_size: {self.sqlite_db_connection.page_size}')
        self.logger.debug(f'foreign_keys: {self.sqlite_db_connection.foreign_keys}')

        if not sqlite_database_existed_before:
            self.logger.debug(f"Creating new database: '{path_to_sqlite_database}'")
            create_tables(self.sqlite_db_connection)
            self.logger.debug("Seed with default values...")
            seed_all_distributions(**seeder_options)
        else:
            self.logger.debug(f"Open existing database: '{path_to_sqlite_database}'")

        return self.sqlite_db_connection

    def delete_database(self, database_name: str) -> None:
        path_to_sqlite_database = self._get_path_to_database(database_name)
        if os.path.isfile(path_to_sqlite_database):
            self.logger.debug(f"Deleting database: '{path_to_sqlite_database}'")
            os.remove(path_to_sqlite_database)
        else:
            raise SqliteDatabaseIsMissingException(path_to_sqlite_database)

    def _load_or_create_sqlite_file_on_hard_drive(
            self, database_name: str, create: bool, reset: bool
    ) -> Tuple[str, bool]:
        path_to_sqlite_database = self._get_path_to_database(database_name)
        sqlite_database_existed_before = os.path.isfile(path_to_sqlite_database)
        if sqlite_database_existed_before:
            if create and not reset:
                raise SqliteDatabaseAlreadyExistsException(path_to_sqlite_database)
            if reset:
                self.logger.debug(f"Deleting old database: '{path_to_sqlite_database}'")
                os.remove(path_to_sqlite_database)
        else:
            if not create:
                raise SqliteDatabaseIsMissingException(path_to_sqlite_database)
            if create:
                self.logger.debug(f"No previous database detected, creating new: '{path_to_sqlite_database}'")
        return path_to_sqlite_database, sqlite_database_existed_before

    def _get_path_to_database(self, database_name: str) -> str:
        return os.path.join(
            self.sqlite_databases_directory,
            database_name
        )
