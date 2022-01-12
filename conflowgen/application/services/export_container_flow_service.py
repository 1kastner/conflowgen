from __future__ import annotations

import enum
import logging
import os
from typing import Dict, Type, Optional
from functools import lru_cache

import numpy as np
import pandas as pd
# noinspection PyProtectedMember
from peewee import ModelSelect

from conflowgen.application.data_types.export_file_format import ExportFileFormat
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.base_model import BaseModel
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Destination
from conflowgen.domain_models.vehicle import DeepSeaVessel, LargeScheduledVehicle, Feeder, Barge, Train, Truck, \
    AbstractLargeScheduledVehicle

EXPORTS_DEFAULT_DIR = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    os.pardir,
    os.pardir,
    "data",
    "exports"
)


class ExportOnlyAllowedToNotExistingFolderException(Exception):
    pass


class CastingException(Exception):
    pass


class ExportContainerFlowService:

    logger = logging.getLogger("conflowgen")

    @classmethod
    @lru_cache(5)
    def debug_once(cls, msg: str):
        cls.logger.debug(msg)

    @classmethod
    def _save_as_csv(cls, df: pd.DataFrame, file_name: str) -> None:
        assert file_name.endswith(".csv")
        # noinspection PyTypeChecker
        df.to_csv(file_name)

    @classmethod
    def _save_as_xls(cls, df: pd.DataFrame, file_name: str):
        assert file_name.endswith(".xls")
        df.to_excel(file_name)

    @classmethod
    def _save_as_xlsx(cls, df: pd.DataFrame, file_name: str):
        assert file_name.endswith(".xlsx")
        df.to_excel(file_name)

    enums_to_convert = (
        ContainerLength,
        StorageRequirement,
        ModeOfTransport
    )

    # For a row, this foreign key is resolved and leads to a flat representation.
    foreign_keys_to_resolve = {
        # Each of barge, feeder, deep sea vessel, and train are treated equally
        **{
            AbstractLargeScheduledVehicle.map_mode_of_transport_to_class(mode_of_transport): {
                'large_scheduled_vehicle': LargeScheduledVehicle
            } for mode_of_transport in ModeOfTransport.get_scheduled_vehicles()
        },
        Truck: {
            'truck_arrival_information_for_delivery': TruckArrivalInformationForDelivery,
            'truck_arrival_information_for_pickup': TruckArrivalInformationForPickup
        },
        Container: {
            'destination': Destination
        }
    }

    # For each row, these column names are dropped, e.g. because the information is irrelevant for further processing,
    # e.g. because it is a foreign key that is already resolved.
    columns_to_drop = {
        Truck: [
            "truck_arrival_information_for_delivery",
            "truck_arrival_information_for_pickup"
        ],
        Container: [
            "destination"
        ],
        LargeScheduledVehicle: [
            "schedule"
        ],
        Destination: [
            "fraction",
            "belongs_to_schedule"
        ]
    }

    columns_to_rename = {
        Container: {
            "sequence_id": "destination_sequence_id"
        }
    }

    def __init__(self):
        self.save_as_file_format_mapping = {
            ExportFileFormat.csv: self._save_as_csv,
            ExportFileFormat.xls: self._save_as_xls,
            ExportFileFormat.xlsx: self._save_as_xlsx
        }

    @classmethod
    def _convert_table_to_pandas_dataframe(
            cls,
            model: Type[BaseModel] | ModelSelect,
            resolved_column: str | None = None
    ) -> pd.DataFrame:

        if resolved_column is not None:
            cls.debug_once(f"This is a nested call to resolve the column '{resolved_column}'")

        # extract data from sql database
        data = list(model.select().dicts())

        if type(model) == ModelSelect:  # pylint: disable=unidiomatic-typecheck  # TODO: check if isinstance works
            model = model.model

        foreign_keys_to_resolve = {}
        if model in cls.foreign_keys_to_resolve.keys():
            foreign_keys_to_resolve = cls.foreign_keys_to_resolve[model]

        # resolve some foreign keys
        for i, row in enumerate(data):
            for column, value in list(row.items()):
                if column not in foreign_keys_to_resolve.keys():  # This is not a foreign key to resolve
                    continue
                if value is None:  # The foreign key points to nothing, thus no resolution
                    continue
                cls.debug_once(f"Resolving column {column} of model {model}...")
                model_of_column = foreign_keys_to_resolve[column]
                nested_model_select = model_of_column.select().where(
                    model_of_column.id == value
                )
                nested_df = cls._convert_table_to_pandas_dataframe(
                    nested_model_select,
                    resolved_column=column
                )  # Recursively resolve the relationship
                assert len(nested_df) == 1, "Only 1:1 relationships between tables are supported"
                nested_values = nested_df.iloc[0]
                for nested_column in nested_df.columns:
                    assert nested_column not in data[i].keys(), "Do not accidentally overwrite a column by a nested " \
                                                                "column"
                    data[i][nested_column] = nested_values[nested_column]

        # convert enums to their value
        for i, row in enumerate(data):
            for column, value in row.items():
                if isinstance(value, cls.enums_to_convert):
                    value: enum.Enum
                    data[i][column] = value.value

        df_table = pd.DataFrame(data)

        # remove any columns that have been (accidentally) inserted, e.g. by resolving foreign keys.
        if model in cls.columns_to_drop:
            columns_to_drop = cls.columns_to_drop[model]
            if not set(columns_to_drop).issubset(set(df_table.columns)):
                missing_columns = set(columns_to_drop) - set(df_table.columns)
                cls.debug_once(f"These columns are listed to be deleted but are missing: {missing_columns}")
                columns_to_drop = set(df_table.columns).intersection(set(columns_to_drop))
            try:
                df_table.drop(columns=columns_to_drop, inplace=True)
            except KeyError as error:
                raise RuntimeError(f"Encountered an exception while dropping columns {columns_to_drop} from model "
                                   f"{model} and the current table columns {df_table.columns}.") from error

        if model in cls.columns_to_rename:
            columns_to_rename = cls.columns_to_rename[model]
            df_table.rename(columns=columns_to_rename, inplace=True)

        # use SQL id instead of newly created pandas id if present
        if len(data) > 0:
            df_table.set_index("id", drop=True, inplace=True)

        # use nullable int instead of float (currently we don't use any floats in the whole application)
        for column in df_table.columns:
            if df_table[column].dtype == np.float64:
                try:
                    df_table[column] = df_table[column].astype("Int64")
                except TypeError as error:
                    raise CastingException(
                        f"Column '{column}' for model '{model.model}' could not be casted from float64 to Int64"
                    ) from error

        return df_table

    @classmethod
    def _convert_sql_database_to_pandas_dataframe(cls) -> Dict[str, pd.DataFrame]:

        df_container = cls._convert_table_to_pandas_dataframe(Container)
        result = {
            "containers": df_container,
        }

        large_schedule_vehicles_as_subtype = {
            "deep_sea_vessels": DeepSeaVessel,
            "feeders": Feeder,
            "barges": Barge,
            "trains": Train,
        }
        for file_name, large_schedule_vehicle_as_subtype in large_schedule_vehicles_as_subtype.items():
            cls.logger.debug(f"Gathering data for generating the '{file_name}' table...")
            df = cls._convert_table_to_pandas_dataframe(large_schedule_vehicle_as_subtype)
            if len(df):
                df.set_index("large_scheduled_vehicle", drop=True, inplace=True)
            else:
                cls.logger.info(f"No content found for the {file_name} table, the file will be empty.")
            result[file_name] = df

        df_trucks = cls._convert_table_to_pandas_dataframe(Truck)
        result["trucks"] = df_trucks
        return result

    def export(self, folder_name: str, path_to_export_folder: Optional[str], file_format: ExportFileFormat):
        """Export container flow to other file formats, simplify internal representation for further processing.
        """
        if path_to_export_folder is None:
            path_to_export_folder = EXPORTS_DEFAULT_DIR
        if not os.path.isdir(path_to_export_folder):
            self.logger.info(f"Creating export folder '{path_to_export_folder}'...")
            os.makedirs(path_to_export_folder, exist_ok=True)
        path_to_target_folder = os.path.join(
            path_to_export_folder,
            folder_name
        )
        if os.path.isdir(path_to_target_folder):
            raise ExportOnlyAllowedToNotExistingFolderException(path_to_target_folder)
        self.logger.info(f"Creating folder '{path_to_target_folder}'...")
        os.mkdir(path_to_target_folder)
        self.logger.info(f"Converting SQL database into file format '.{file_format.value}'")
        dfs = self._convert_sql_database_to_pandas_dataframe()
        for file_name, df in dfs.items():
            full_file_name = file_name + "." + file_format.value
            path_to_file = os.path.join(
                path_to_folder,
                full_file_name
            )
            self.logger.debug(f"Saving file '{full_file_name}'...")
            # noinspection PyArgumentList
            self.save_as_file_format_mapping[file_format](df, path_to_file)
        self.logger.info("Export has finished successfully.")
