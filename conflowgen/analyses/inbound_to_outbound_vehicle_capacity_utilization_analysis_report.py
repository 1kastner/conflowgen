from __future__ import annotations

import datetime
import typing

import matplotlib.pyplot as plt
import matplotlib.ticker
import matplotlib.figure
import pandas as pd

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.inbound_to_outbound_vehicle_capacity_utilization_analysis import \
    InboundToOutboundVehicleCapacityUtilizationAnalysis, VehicleIdentifier
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph


class InboundToOutboundVehicleCapacityUtilizationAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.InboundToOutboundCapacityUtilizationAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    The visual and table are expected to approximately look like in the
    `example InboundToOutboundVehicleCapacityUtilizationAnalysisReport \
    <notebooks/analyses.ipynb#Inbound-To-Outbound-Vehicle-Capacity-Utilization-Analysis-Report>`_.
    """

    report_description = """
    Analyze the used vehicle capacity for each vehicle for the inbound and outbound journeys.
    Generally, it expected to reach an equilibrium - each vehicle should approximately pick up as many containers
    at the container terminal as it has delivered.
    Great disparities between the transported capacities on the inbound and outbound journey are considered noteworthy
    but depending on the input data it might be acceptable.
    Trucks are excluded from this analysis.
    """

    plot_title = "Capacity utilization analysis"

    def __init__(self):
        super().__init__()
        self._end_date = None
        self._start_date = None
        self._vehicle_type_description = None
        self.vehicle_type_description = None
        self.analysis = InboundToOutboundVehicleCapacityUtilizationAnalysis(
            transportation_buffer=self.transportation_buffer
        )
        self._df = None

    def get_report_as_text(self, **kwargs) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.

        Keyword Args:
            vehicle_type (:py:obj:`Any`): Either ``"scheduled vehicles"``, a single vehicle of type
                :class:`.ModeOfTransport` or a whole collection of vehicle types, e.g., passed as a :class:`list` or
                :class:`set`.
                For the exact interpretation of the parameter, check
                :class:`.InboundToOutboundVehicleCapacityUtilizationAnalysis`.
            start_date (datetime.datetime):
                Only include containers that arrive after the given start time.
            end_date (datetime.datetime):
                Only include containers that depart before the given end time.

        Returns:
             The report in text format spanning over several lines.
        """
        capacities, vehicle_type_description, start_date, end_date = self._get_analysis(kwargs)
        assert len(kwargs) == 0, f"Keyword(s) {list(kwargs.keys())} have not been processed."

        report = "\n"
        report += "vehicle type = " + vehicle_type_description + "\n"
        report += f"start date = {self._get_datetime_representation(start_date)}\n"
        report += f"end date = {self._get_datetime_representation(end_date)}\n"
        report += "vehicle identifier                                 "
        report += "inbound volume (in TEU) "
        report += "outbound volume (in TEU)"
        report += "\n"
        for vehicle_identifier, (used_inbound_capacity, used_outbound_capacity) in capacities.items():
            vehicle_name = self._vehicle_identifier_to_text(vehicle_identifier)
            report += f"{vehicle_name:<50} "  # align this with cls.maximum_length_for_readable_name!
            report += f"{used_inbound_capacity:>23.1f} "
            report += f"{used_outbound_capacity:>24.1f}"
            report += "\n"
        if len(capacities) == 0:
            report += "--no vehicles exist--\n"
        else:
            report += "(rounding errors might exist)\n"
        return report

    def _get_analysis(self, kwargs) -> typing.Tuple[
        typing.Dict[VehicleIdentifier, typing.Tuple[float, float]],
        str,
        datetime.datetime,
        datetime.datetime
    ]:
        vehicle_type_any = kwargs.pop("vehicle_type", "scheduled vehicles")
        start_date = kwargs.pop("start_date", None)
        end_date = kwargs.pop("end_date", None)

        capacities = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle(
            vehicle_type=vehicle_type_any,
            start_date=start_date,
            end_date=end_date
        )
        vehicle_type_description: str = self._get_enum_or_enum_set_representation(vehicle_type_any, ModeOfTransport)

        return capacities, vehicle_type_description, start_date, end_date

    def get_report_as_graph(self, **kwargs) -> matplotlib.figure.Figure:
        """
        The report as a graph is represented as a scatter plot using pandas.

        Keyword Args:
            plot_type (:obj:`str`): Either ``"absolute"``, ``"relative"``, ``"absolute and relative"``, ``"over time"``,
                or ``"all"``. Defaults to "all".
            vehicle_type (:obj:`Any`): Either ``"all"``, a single vehicle of type :class:`.ModeOfTransport` or a
                whole collection of vehicle types, e.g., passed as a :class:`list` or :class:`set`.
                For the exact interpretation of the parameter, check
                :class:`.InboundToOutboundVehicleCapacityUtilizationAnalysis`.
                Defaults to ``"all"``.
            start_date (datetime.datetime):
                Only include containers that arrive after the given start time. Defaults to ``None``.
            end_date (datetime.datetime):
                Only include containers that depart before the given end time. Defaults to ``None``.
        Returns:
             The matplotlib figure
        """
        # kwargs for plot
        plot_type = kwargs.pop("plot_type", "all")

        # kwargs for report
        capacities, vehicle_type_description, start_date, end_date = self._get_analysis(kwargs)
        self._vehicle_type_description = vehicle_type_description
        self._start_date = start_date
        self._end_date = end_date

        assert len(kwargs) == 0, f"Keyword(s) {list(kwargs.keys())} have not been processed."

        if len(capacities) == 0:
            fig, ax = no_data_graph()
            ax.set_title(self.plot_title)
            return fig

        self._df = self._convert_analysis_to_df(capacities)

        if plot_type == "absolute":
            fig, ax = plt.subplots(1, 1)
            self._plot_absolute_values(ax=ax)
        elif plot_type == "relative":
            fig, ax = plt.subplots(1, 1)
            self._plot_relative_values(ax=ax)
        elif plot_type == "absolute and relative":
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
            self._plot_absolute_values(ax=ax1)
            self._plot_relative_values(ax=ax2)
            plt.subplots_adjust(wspace=0.4)
        elif plot_type == "over time":
            fig, ax = plt.subplots(1, 1)
            self._plot_relative_values_over_time(ax=ax)
        elif plot_type == "all":
            fig = plt.figure(figsize=(10, 10))
            gs = fig.add_gridspec(2, 2)
            ax1 = fig.add_subplot(gs[0, 0])
            ax2 = fig.add_subplot(gs[0, 1])
            ax3 = fig.add_subplot(gs[1, :])
            self._plot_absolute_values(ax=ax1)
            self._plot_relative_values(ax=ax2)
            self._plot_relative_values_over_time(ax=ax3)
            fig.tight_layout(pad=5.0)
        else:
            raise Exception(f"Plot type '{plot_type}' is not supported.")

        plt.legend(
            loc='lower left',
            bbox_to_anchor=(1, 0),
            fancybox=True,
        )
        return fig

    def _plot_absolute_values(
            self,
            ax: typing.Optional[matplotlib.pyplot.axis] = None
    ) -> matplotlib.pyplot.axis:
        ax = self._df.plot.scatter(x="inbound volume (in TEU)", y="outbound volume (in TEU)", ax=ax)
        slope = 1 + self.transportation_buffer
        ax.axline((0, 0), slope=slope, color='black', label='outbound capacity (in TEU)')
        ax.axline((0, 0), slope=1, color='gray', label='equilibrium')
        ax.set_title(self.plot_title + " (absolute),\n" + self._get_filter_values(
            self._vehicle_type_description, self._start_date, self._end_date)
                     )
        ax.set_aspect('equal', adjustable='box')
        ax.grid(color='lightgray', linestyle=':', linewidth=.5)
        maximum = self._df[["inbound volume (in TEU)", "outbound volume (in TEU)"]].max(axis=1).max(axis=0)
        axis_limitation = maximum * 1.1  # add some white space to the top and left
        ax.set_xlim([0, axis_limitation])
        ax.set_ylim([0, axis_limitation])
        return ax

    def _get_filter_values(
            self,
            vehicle_type: str,
            start_date: datetime.datetime | None,
            end_date: datetime.datetime | None
    ) -> str:
        filter_values = f"vehicle type = {vehicle_type}\n"
        filter_values += f"start date = {self._get_datetime_representation(start_date)}\n"
        filter_values += f"end date = {self._get_datetime_representation(end_date)}"

        return filter_values

    def _plot_relative_values(
            self,
            ax: typing.Optional[matplotlib.pyplot.axis] = None
    ) -> matplotlib.pyplot.axis:
        ax = self._df.plot.scatter(x="inbound volume (in TEU)", y="ratio", ax=ax)
        ax.axline((0, (1 + self.transportation_buffer)), slope=0, color='black', label='outbound capacity (in TEU)')
        ax.axline((0, 1), slope=0, color='gray', label='equilibrium')
        ax.set_title(self.plot_title + " (relative),\n" + self._get_filter_values(
            self._vehicle_type_description, self._start_date, self._end_date)
                     )
        ax.grid(color='lightgray', linestyle=':', linewidth=.5)
        return ax

    def _plot_relative_values_over_time(
            self,
            ax: typing.Optional[matplotlib.pyplot.axis] = None
    ) -> matplotlib.pyplot.axis:
        ax = self._df.plot.scatter(x="arrival time", y="ratio", ax=ax)
        df_arrival_time = self._df.set_index("arrival time")
        df_arrival_time["ratio"].rename("ratio outbound to inbound volume (in TEU)", inplace=True)
        df_arrival_time["equilibrium"].plot(ax=ax, color="gray")
        df_arrival_time["outbound capacity (in TEU)"].plot(ax=ax, color="black")
        ax.set_title(self.plot_title + " (over time),\n" + self._get_filter_values(
            self._vehicle_type_description, self._start_date, self._end_date)
                     )
        ax.grid(color='lightgray', linestyle=':', linewidth=.5)
        return ax

    def _convert_analysis_to_df(
            self,
            capacities: typing.Dict[VehicleIdentifier, typing.Tuple[float, float]]
    ) -> pd.DataFrame:
        rows = []
        for vehicle_identifier, (inbound_capacity, used_outbound_capacity) in capacities.items():
            vehicle_name = self._vehicle_identifier_to_text(vehicle_identifier)
            rows.append({
                "vehicle name": vehicle_name,
                "vehicle type": vehicle_identifier.mode_of_transport,
                "arrival time": vehicle_identifier.vehicle_arrival_time,
                "inbound volume (in TEU)": inbound_capacity,
                "outbound volume (in TEU)": used_outbound_capacity,
                "equilibrium": 1,
                "outbound capacity (in TEU)": 1 + self.transportation_buffer
            })
        df = pd.DataFrame(rows)
        df["ratio"] = df["outbound volume (in TEU)"] / df["inbound volume (in TEU)"]
        return df
