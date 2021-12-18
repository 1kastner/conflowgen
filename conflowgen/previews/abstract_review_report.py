from __future__ import annotations

import abc
import datetime

from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class AbstractPreviewReport(abc.ABC):

    order_of_vehicle_types_in_report = [
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder,
        ModeOfTransport.barge,
        ModeOfTransport.train,
        ModeOfTransport.truck
    ]

    def __init__(self):
        assert set(self.order_of_vehicle_types_in_report) == set(ModeOfTransport), "Missing ModeOfTransport type"
        self.start_date: datetime.date | None = None
        self.end_date: datetime.date | None = None
        self.transportation_buffer: float | None = None
        self.container_flow_generation_properties_repository = ContainerFlowGenerationPropertiesRepository()
        self.reload()

    def reload(self):
        properties = self.container_flow_generation_properties_repository.get_container_flow_generation_properties()
        self.start_date = properties.start_date
        self.end_date = properties.end_date
        assert self.start_date is not None
        assert self.end_date is not None
        assert self.start_date < self.end_date
        self.transportation_buffer = properties.transportation_buffer
        assert -1 < self.transportation_buffer

    @abc.abstractmethod
    def get_report_as_text(self) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.

        Returns: The report in text format (possibly spanning over several lines).
        """
        return ""

    def get_report_as_graph(self) -> object:
        raise NotImplementedError("No graph representation of this report has yet been defined.")
