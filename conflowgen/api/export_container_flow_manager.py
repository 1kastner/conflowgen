from __future__ import annotations

from typing import Optional

from conflowgen.application.services.export_container_flow_service import \
    ExportContainerFlowService
from conflowgen.application.data_types.export_file_format import ExportFileFormat


class ExportContainerFlowManager:
    """
    In the SQLite databases all data is stored. This might not be the right format for further usage though. This
    manager provides the interface to export the container flow, excluding the input distributions etc., so that they
    can be read in easily for the next step, e.g. a routine in a simulation model or mathematical optimization script.
    """

    def __init__(self):
        self.service = ExportContainerFlowService()

    def export(
            self,
            folder_name: str,
            path_to_export_folder: Optional[str] = None,
            file_format: Optional[ExportFileFormat] = None,
            overwrite: bool = False
    ) -> str:
        """
        This extracts the container movement data from the SQL database to a folder of choice in a tabular data format.

        Args:
            folder_name: Name of folder that bundles the tabular data which belongs together
            path_to_export_folder: Path to directory where all exports are kept,
                defaults to ``<project root>/data/exports/``
            file_format: Desired tabular format, defaults to :class:`ExportFileFormat.csv`.
            overwrite: Whether to overwrite previously exported data, defaults to False

        Returns:
            The path to the folder where the tabular data is located
        """
        if file_format is None:
            file_format = ExportFileFormat.csv
        path_to_target_folder = self.service.export(
            folder_name=folder_name,
            path_to_export_folder=path_to_export_folder,
            file_format=file_format,
            overwrite=overwrite
        )
        return path_to_target_folder
