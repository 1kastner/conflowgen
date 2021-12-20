import logging
import os
from typing import List

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
    """
    def __init__(self, sqlite_databases_directory=None):
        self.logger = logging.getLogger("conflowgen")
        if sqlite_databases_directory is None:
            self.sqlite_databases_directory = os.path.join(
                os.path.dirname(os.path.realpath(__file__)),
                os.pardir,
                "data",
                "databases"
            )
        else:
            self.sqlite_databases_directory = sqlite_databases_directory
        self.sqlite_db_connection = None

    def list_all_sqlite_databases(self) -> List[str]:
        """
        Returns: A list of all SQLite databases in the path '<PROJECTROOT>/data/databases/'
        """
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
        path_to_sqlite_database = os.path.join(
            self.sqlite_databases_directory,
            database_name
        )
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

        self.sqlite_db_connection = SqliteDatabase(
            path_to_sqlite_database,
            pragmas={
                # compare with recommended settings from
                # https://docs.peewee-orm.com/en/latest/peewee/database.html
                'journal_mode': 'wal',
                'cache_size': -32 * 1024,  # counted in KiB, thus this means 32MB cache
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0
            }
        )
        database_proxy.initialize(self.sqlite_db_connection)
        self.sqlite_db_connection.connect()

        self.logger.info(f'journal_mode: {self.sqlite_db_connection.journal_mode}')
        self.logger.info(f'cache_size: {self.sqlite_db_connection.cache_size}')
        self.logger.info(f'page_size: {self.sqlite_db_connection.page_size}')
        self.logger.info(f'foreign_keys: {self.sqlite_db_connection.foreign_keys}')

        if not sqlite_database_existed_before:
            self.logger.debug(f"Creating new database: '{path_to_sqlite_database}'")
            create_tables(self.sqlite_db_connection)
            self.logger.debug("Seed with default values...")
            seed_all_distributions(**seeder_options)
        else:
            self.logger.debug(f"Open existing database: '{path_to_sqlite_database}'")

        return self.sqlite_db_connection

    def delete_database(self, database_name: str) -> None:
        """
        Args:
            database_name: The file name of the SQLite database to delete
        """
        path_to_sqlite_database = os.path.join(
            self.sqlite_databases_directory,
            database_name
        )
        if os.path.isfile(path_to_sqlite_database):
            self.logger.debug(f"Deleting database: '{path_to_sqlite_database}'")
            os.remove(path_to_sqlite_database)
        else:
            raise SqliteDatabaseIsMissingException(path_to_sqlite_database)
