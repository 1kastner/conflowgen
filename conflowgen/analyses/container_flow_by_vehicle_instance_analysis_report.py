from __future__ import annotations

import logging
import typing

import matplotlib.figure
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from conflowgen.analyses.container_flow_by_vehicle_instance_analysis import ContainerFlowByVehicleInstanceAnalysis
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph


class ContainerFlowByVehicleInstanceAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.ContainerFlowByVehicleInstanceAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    The visual and table are expected to approximately look like in the
    `example ContainerFlowByVehicleInstanceAnalysisReport \
    <notebooks/analyses.ipynb#Container-Flow-By-Vehicle-Instance-Analysis-Report>`_.
    """

    report_description = """
    Analyze how many import, export, and transshipment containers were unloaded and loaded on each vehicle.
    """

    logger = logging.getLogger("conflowgen")

    def __init__(self):
        super().__init__()
        self._df = None
        self.analysis = ContainerFlowByVehicleInstanceAnalysis()

    def get_report_as_text(
            self,
            vehicle_types: ModeOfTransport | str | typing.Collection = "scheduled vehicles",
            **kwargs
    ) -> str:
        """
        Keyword Args:
            vehicle_types (typing.Collection[ModeOfTransport]): A collection of vehicle types, e.g., passed as a
                :class:`list` or :class:`set`.
                Only the vehicles that correspond to the provided vehicle type(s) are considered in the analysis.
            start_date (datetime.datetime): The earliest arriving container that is included.
                Consider all containers if :obj:`None`.
            end_date (datetime.datetime): The latest departing container that is included.
                Consider all containers if :obj:`None`.

        Returns:
            The report in human-readable text format
        """
        plain_table, vehicle_types = self._get_analysis(kwargs)

        if len(plain_table) > 0:
            df = self._get_dataframe_from_plain_table(plain_table)
            report = str(df)
        else:
            report = "(no report feasible because no data is available)"

        return report

    def _get_analysis(self, kwargs: dict) -> (list, list):
        start_date = kwargs.pop("start_date", None)
        end_date = kwargs.pop("end_date", None)
        vehicle_types = kwargs.pop("vehicle_types", (
                ModeOfTransport.train,
                ModeOfTransport.feeder,
                ModeOfTransport.deep_sea_vessel,
                ModeOfTransport.barge
            ))

        assert len(kwargs) == 0, f"Keyword(s) {kwargs.keys()} have not been processed"

        container_flow = self.analysis.get_container_flow_by_vehicle(
            vehicle_types=vehicle_types,
            start_date=start_date,
            end_date=end_date,
        )

        vehicle_types = list(container_flow.keys())

        plain_table = []

        for mode_of_transport in vehicle_types:
            for vehicle_identifier in container_flow[mode_of_transport].keys():
                for flow_direction in container_flow[mode_of_transport][vehicle_identifier]:
                    for journey_direction in container_flow[mode_of_transport][vehicle_identifier][flow_direction]:
                        handled_volume = container_flow[
                            mode_of_transport][vehicle_identifier][flow_direction][journey_direction]

                        plain_table.append(
                            (mode_of_transport, vehicle_identifier.id, vehicle_identifier.vehicle_name,
                             vehicle_identifier.service_name, vehicle_identifier.vehicle_arrival_time,
                             str(flow_direction), journey_direction, handled_volume)
                        )

        return plain_table, vehicle_types

    def get_report_as_graph(self, **kwargs) -> matplotlib.figure.Figure:
        """
        Keyword Args:
            vehicle_types (typing.Collection[ModeOfTransport]): A collection of vehicle types, e.g., passed as a
                :class:`list` or :class:`set`.
                Only the vehicles that correspond to the provided vehicle type(s) are considered in the analysis.
            start_date (datetime.datetime):
                The earliest arriving container that is included. Consider all containers if :obj:`None`.
            end_date (datetime.datetime):
                The latest departing container that is included. Consider all containers if :obj:`None`.

        Returns:
            Grouped by vehicle type and vehicle instance, how many import, export, and transshipment containers are
            unloaded and loaded (measured in TEU).
        """
        plain_table, vehicle_types = self._get_analysis(kwargs)

        plot_title = "Container Flow By Vehicle Instance Analysis Report"

        if len(plain_table) == 0:
            fig, ax = no_data_graph()
            ax.set_title(plot_title)
            return fig

        df = self._get_dataframe_from_plain_table(plain_table)

        number_subplots = 2 * len(vehicle_types)
        fig, axes = plt.subplots(nrows=number_subplots, figsize=(7, 4 * number_subplots))
        i = 0
        for mode_of_transport in vehicle_types:
            for journey_direction in ["inbound", "outbound"]:
                ax = axes[i]
                i += 1
                ax.set_title(f"{str(mode_of_transport).replace('_', ' ').capitalize()} - {journey_direction}")
                df[(df["mode_of_transport"] == mode_of_transport)
                   & (df["journey_direction"] == journey_direction)
                   ].groupby("flow_direction")["handled_volume"].plot(ax=ax, linestyle=":", marker=".")
                ax.set_ylabel("")

        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

        plt.tight_layout()

        return fig

    def _get_dataframe_from_plain_table(self, plain_table):
        column_names = ("mode_of_transport", "vehicle_id", "vehicle_name", "service_name", "vehicle_arrival_time",
                        "flow_direction", "journey_direction", "handled_volume")
        df = pd.DataFrame(plain_table)
        df.columns = column_names
        df.set_index("vehicle_arrival_time", inplace=True)
        df.replace(0, np.nan, inplace=True)
        self._df = df
        return df
