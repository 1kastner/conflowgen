from __future__ import annotations

import abc
import datetime
import enum
import logging
import tempfile
import typing
from collections.abc import Iterable

import matplotlib.pyplot as plt
import plotly.graph_objects
from matplotlib import image as mpimg

from conflowgen.descriptive_datatypes import VehicleIdentifier
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class AbstractReport(abc.ABC):

    #: Each report can log to the console
    logger = logging.getLogger("conflowgen")

    #: Some entries are too long to be printed to console, such as vehicle identifiers
    maximum_length_for_readable_name = 50

    #: The default order in which vehicle types are reported. If desired, this can be altered.
    order_of_vehicle_types_in_report = [
        ModeOfTransport.deep_sea_vessel,
        ModeOfTransport.feeder,
        ModeOfTransport.barge,
        ModeOfTransport.train,
        ModeOfTransport.truck
    ]

    #: The days of the week
    days_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    @property
    @abc.abstractmethod
    def report_description(self) -> str:
        """The report description is a text representation describing a preview report. It is formatted to allow being
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
        assert self.start_date is not None, "A start date needs to be set."
        assert self.end_date is not None, "An end date needs to be set."
        assert self.start_date < self.end_date, "The start date needs to be before the end date."
        self.transportation_buffer = properties.transportation_buffer
        assert -1 < self.transportation_buffer, "The transportation buffer needs to be larger than -100%."

    @abc.abstractmethod
    def get_report_as_text(self, **kwargs) -> str:
        """
        The report as a text is represented as a table suitable for logging.
        It uses a human-readable formatting style.
        The additional keyword arguments are passed to the analysis instance in case it accepts them.

        Returns:
             The report in text format (possibly spanning over several lines).
        """
        pass

    @abc.abstractmethod
    def get_report_as_graph(self, **kwargs) -> object:
        """
        The report as a graph is represented in a figure.
        The additional keyword arguments are passed to the analysis instance in case it accepts them.

        Returns:
             A reference to the figure. The actual type depends on the plotting library.
        """
        pass

    @abc.abstractmethod
    def show_report_as_graph(self, **kwargs) -> None:
        """
        This method first invokes ``.get_report_as_graph()`` and then it displays the graph object, e.g., by invoking
        ``plt.show()`` or ``fig.show()``.
        This depends on the visualisation library.
        The additional keyword arguments are passed to the analysis instance in case it accepts them.
        """
        pass

    @staticmethod
    def _get_enum_or_enum_set_representation(enum_or_enum_set: typing.Any, enum_type: typing.Type[enum.Enum]) -> str:
        if enum_or_enum_set is None or enum_or_enum_set == "all":
            return "all"
        if isinstance(enum_or_enum_set, str):
            return enum_or_enum_set
        if isinstance(enum_or_enum_set, enum_type):  # a
            return str(enum_or_enum_set)
        if isinstance(enum_or_enum_set, Iterable):  # a & b & c
            return " & ".join([str(element) for element in enum_or_enum_set])
        return str(enum_or_enum_set)  # just give it a try

    def _get_vehicle_representation(self, vehicle_type: typing.Any) -> str:
        return self._get_enum_or_enum_set_representation(vehicle_type, ModeOfTransport)

    def _get_storage_requirement_representation(self, storage_requirement: typing.Any) -> str:
        return self._get_enum_or_enum_set_representation(storage_requirement, StorageRequirement)

    @staticmethod
    def _get_datetime_representation(datetime_object: datetime.datetime | None):
        if datetime_object is None:
            return "none"
        return datetime_object.replace(second=0, microsecond=0).isoformat()

    @classmethod
    def _vehicle_identifier_to_text(cls, vehicle_identifier: VehicleIdentifier) -> str:
        if vehicle_identifier.mode_of_transport != ModeOfTransport.truck:
            name = f"{vehicle_identifier.mode_of_transport}-{vehicle_identifier.service_name}" \
                   f"-{vehicle_identifier.vehicle_name}"
        else:
            arrival_time = vehicle_identifier.vehicle_arrival_time.replace(microsecond=0)
            name = f"{vehicle_identifier.mode_of_transport}-{arrival_time}"
        if len(name) > cls.maximum_length_for_readable_name:
            name = name[:46] + "..."

        return name


class AbstractReportWithMatplotlib(AbstractReport, metaclass=abc.ABCMeta):

    def show_report_as_graph(self, **kwargs) -> None:

        # All matplotlib reports are currently static in the sense that they do not require additional libraries to work
        # on a webpage such as the documentation. We can simply ignore this keyword.
        kwargs.pop("static", None)
        kwargs.pop("display_as_ipython_svg", None)

        with plt.style.context('seaborn-colorblind'):
            self.get_report_as_graph(**kwargs)
            plt.show(block=True)


class AbstractReportWithPlotly(AbstractReport, metaclass=abc.ABCMeta):
    def show_report_as_graph(self, **kwargs) -> None:
        """
        Plotly needs quite some libraries loaded in the online documentation so that the figures are actually visible
        to the user.
        With the two keywords ``static`` and ``display_as_ipython_svg``, alternative means of visualization can be
        selected.
        Additional keywords are passed on to the report.

        Keyword Args:
            static (bool): Whether to convert the interactive plotly plots into static images.
            display_as_ipython_svg (bool): Whether to convert the interactive plots into SVG and display it with IPython
        """
        static = kwargs.pop("static", False)
        display_as_ipython_svg = kwargs.pop("display_as_ipython_svg", False)

        figs: typing.Any = self.get_report_as_graph(**kwargs)
        try:
            len(figs)
        except TypeError:  # there is only one
            figs = [figs]

        for fig in figs:
            if static:  # show as PNG or similar
                self._show_static_fig(fig)
            if display_as_ipython_svg:  # use IPython SVG functionality (e.g., in browser)
                self._display_ipython_svg(fig)
            if not static and not display_as_ipython_svg:  # the default way chosen by plotly
                fig.show()

    @staticmethod
    def _display_ipython_svg(fig: plotly.graph_objects.Figure) -> None:
        import IPython.display  # pylint: disable=import-outside-toplevel
        svg_format_image = fig.to_image(format="svg", width=800)
        IPython.display.display(IPython.display.SVG(svg_format_image))

    @staticmethod
    def _show_static_fig(fig: plotly.graph_objects.Figure) -> None:
        png_format_image = fig.to_image(format="png", width=800)
        with tempfile.NamedTemporaryFile() as _file:
            _file.write(png_format_image)
            img = mpimg.imread(_file)
        plt.figure(figsize=(20, 10))
        plt.imshow(img)
        plt.axis('off')
        plt.show(block=True)
