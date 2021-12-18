from __future__ import annotations

from conflowgen.flow_generator.export_container_flow_service import \
    ExportContainerFlowService
from conflowgen.application_models.data_types.export_file_format import ExportFileFormat


class ExportContainerFlowManager:
    """
    In the SQLite databases all data is stored. This might not be the right format for further usage though. This
    manager allows to export the container flow, excluding the input distributions etc., so that they can be read in
    for the next step easily, e.g. a routine in a simulation model or mathematical optimization script.
    """

    def __init__(self):
        self.service = ExportContainerFlowService()

    def export(
            self,
            folder_name: str,
            file_format: ExportFileFormat | None = None
    ) -> None:
        """
        This extracts the container movement data from the SQL database to a folder of choice in a tabular data format.

        Args:
            folder_name: Name of folder in ``<project root>/data/exports/``
            file_format: Desired tabular format
        """
        if file_format is None:
            file_format = ExportFileFormat.csv
        self.service.export(folder_name, file_format)
