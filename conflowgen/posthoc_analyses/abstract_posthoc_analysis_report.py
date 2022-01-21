import abc
from typing import cast

from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class AbstractPosthocAnalysisReport(abc.ABC):

    @property
    @abc.abstractmethod
    def report_description(self) -> str:
        """The report description is a text representation describing an analysis report. It is formatted to allow being
        logged to a command line interface or a file. This short description does not contain all information available.
        If in doubt, the user should return to the documentation."""

    order_of_vehicle_types_in_report = [
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder,
        ModeOfTransport.barge,
        ModeOfTransport.train,
        ModeOfTransport.truck
    ]

    def __init__(self):
        self.container_flow_generation_properties_repository = ContainerFlowGenerationPropertiesRepository()
        self.transportation_buffer = None
        self.reload()

    def reload(self):
        properties = self.container_flow_generation_properties_repository.get_container_flow_generation_properties()
        self.transportation_buffer = properties.transportation_buffer
        assert -1 < self.transportation_buffer

    @abc.abstractmethod
    def get_report_as_text(self) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.

        Returns: The report in text format (possibly spanning over several lines).
        """
        ...

    def get_report_as_graph(self, **kwargs) -> object:
        """
        The report as a graph can be implemented by different visualisation libraries.
        If you just want to get the visuals without caring about the underlying library, invoke
        ``.show_report_as_graph()`` instead.

        Args:
            **kwargs: The additional keyword arguments are passed to the analysis instance.

        Returns:
            The report as a plottable graph object (the plotting command has not yet been invoked).
        """
        raise NotImplementedError("No graph representation of this report has yet been defined.")

    def show_report_as_graph(self, **kwargs) -> None:
        """
        This method first invokes ``.get_report_as_graph()`` and then it displays the graph object, e.g. by invoking
        ``plt.show()`` or ``fig.show``. This depends on the visualisation library.

        Args:
            **kwargs: The additional keyword arguments are passed to the analysis instance.
        """
        raise NotImplementedError("No show method has yet been defined.")


class AbstractPosthocAnalysisReportWithMatplotlib(AbstractPosthocAnalysisReport, metaclass=abc.ABCMeta):
    def show_report_as_graph(self, **kwargs) -> None:
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
        self.get_report_as_graph()
        plt.show()


class AbstractPosthocAnalysisReportWithPlotly(AbstractPosthocAnalysisReport, metaclass=abc.ABCMeta):
    def show_report_as_graph(self, **kwargs) -> None:
        import plotly.graph_objects as go  # pylint: disable=import-outside-toplevel
        fig: go.Figure = cast(go.Figure, self.get_report_as_graph())
        fig.show()
