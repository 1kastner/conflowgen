from __future__ import annotations

import abc
import datetime
import tempfile
from typing import cast

import matplotlib.pyplot as plt
from matplotlib import image as mpimg

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

    @property
    @abc.abstractmethod
    def report_description(self) -> str:
        """The report description is a text representation describing an preview report. It is formatted to allow being
        logged to a command line interface or a file. This short description does not contain all information available.
        If in doubt, the user should return to the documentation."""

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

    def show_report_as_graph(self, **kwargs) -> None:
        """
        This method first invokes ``.get_report_as_graph()`` and then it displays the graph object, e.g. by invoking
        ``plt.show()`` or ``fig.show``. This depends on the visualisation library.

        Args:
            **kwargs: The additional keyword arguments are passed to the analysis instance.
        """
        raise NotImplementedError("No show method has yet been defined.")


class AbstractPreviewReportWithMatplotlib(AbstractPreviewReport, metaclass=abc.ABCMeta):
    def show_report_as_graph(self, **kwargs) -> None:
        self.get_report_as_graph()
        plt.show()


class AbstractPreviewReportWithPlotly(AbstractPreviewReport, metaclass=abc.ABCMeta):
    def show_report_as_graph(self, **kwargs) -> None:
        import plotly.graph_objects as go  # pylint: disable=import-outside-toplevel
        fig: go.Figure = cast(go.Figure, self.get_report_as_graph())
        if "static" in kwargs and kwargs["static"]:
            png_format_image = fig.to_image(format="png", width=800)
            with tempfile.NamedTemporaryFile() as _file:
                _file.write(png_format_image)
                img = mpimg.imread(_file)
            plt.figure(figsize=(20, 10))
            plt.imshow(img)
            plt.axis('off')
            plt.show()
        else:
            fig.show()
