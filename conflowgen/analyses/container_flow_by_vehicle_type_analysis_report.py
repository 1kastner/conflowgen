from __future__ import annotations

import itertools
import logging
from collections.abc import Collection
from typing import Dict

import plotly.graph_objects

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.analyses.container_flow_by_vehicle_type_analysis import ContainerFlowByVehicleTypeAnalysis
from conflowgen.reporting import AbstractReportWithPlotly


class ContainerFlowByVehicleTypeAnalysisReport(AbstractReportWithPlotly):
    """
    This analysis report takes the data structure as generated by :class:`.ContainerFlowByVehicleTypeAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    """

    report_description = """
    Analyze how many containers were delivered by which vehicle type and how their journey continued. The analysis pairs
    the inbound and outbound journey for each container.
    """

    logger = logging.getLogger("conflowgen")

    def __init__(self):
        super().__init__()
        self.analysis = ContainerFlowByVehicleTypeAnalysis()

    def get_report_as_text(
            self, **kwargs
    ) -> str:
        """
        Keyword Args:
            unit (str): One of "teu", "container", or "both". Defaults to "both" if none provided.
            start_date (datetime.datetime): The earliest arriving container that is included.
                Consider all containers if :obj:`None`.
            end_date (datetime.datetime): The latest departing container that is included.
                Consider all containers if :obj:`None`.

        Returns:
            The report in human-readable text format
        """
        unit = kwargs.pop("unit", "both")
        assert len(kwargs) == 0, f"No further keyword arguments supported for {self.__class__.__name__} but received " \
                                 f"{kwargs}"

        inbound_to_outbound_flow = self.analysis.get_inbound_to_outbound_flow()

        report = ""

        if unit == "TEU":
            report += self._generate_report_for_unit(inbound_to_outbound_flow.teu, unit=unit)
        elif unit == "containers":
            report += self._generate_report_for_unit(inbound_to_outbound_flow.containers, unit=unit)
        elif unit == "both":
            report += self._generate_report_for_unit(inbound_to_outbound_flow.teu, unit="TEU")
            report += "\n"
            report += self._generate_report_for_unit(inbound_to_outbound_flow.containers, unit="containers")
        else:
            raise ValueError(f"Unknown unit '{unit}'")

        # create string representation
        return report

    def _generate_report_for_unit(
            self,
            inbound_to_outbound_flow: Dict[ModeOfTransport, Dict[ModeOfTransport, float]],
            unit: str
    ):
        report = "\n"
        report += "vehicle type (from) "
        report += "vehicle type (to) "
        report += f"transported capacity (in {unit})"
        report += "\n"
        for vehicle_type_from, vehicle_type_to in itertools.product(self.order_of_vehicle_types_in_report, repeat=2):
            vehicle_type_from_as_text = str(vehicle_type_from).replace("_", " ")
            vehicle_type_to_as_text = str(vehicle_type_to).replace("_", " ")
            report += f"{vehicle_type_from_as_text:<19} "
            report += f"{vehicle_type_to_as_text:<18} "
            report += f"{inbound_to_outbound_flow[vehicle_type_from][vehicle_type_to]:>28.1f}"
            report += "\n"
        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self, **kwargs) -> Collection[plotly.graph_objects.Figure]:
        """
        The container flow is represented by a Sankey diagram.

        Keyword Args:
            unit (str): One of "TEU", "containers", or "both". Defaults to "both" if none provided.

        Returns:
             The plotly figure(s) of the Sankey diagram.
        """
        unit = kwargs.pop("unit", "both")
        assert len(kwargs) == 0, f"No further keyword arguments supported for {self.__class__.__name__} but received " \
                                 f"{kwargs}"

        inbound_to_outbound_flow = self.analysis.get_inbound_to_outbound_flow()

        figs = []

        if unit == "TEU":
            figs += [self._plot_inbound_to_outbound_flow(inbound_to_outbound_flow.teu, unit=unit)]
        elif unit == "containers":
            figs += [self._plot_inbound_to_outbound_flow(inbound_to_outbound_flow.containers, unit=unit)]
        elif unit == "both":
            figs += [self._plot_inbound_to_outbound_flow(inbound_to_outbound_flow.teu, unit="TEU")]
            figs += [self._plot_inbound_to_outbound_flow(inbound_to_outbound_flow.containers, unit="containers")]
        else:
            raise ValueError(f"Unknown unit '{unit}'")
        return figs

    def _plot_inbound_to_outbound_flow(
            self,
            inbound_to_outbound_flow: Dict[ModeOfTransport, Dict[ModeOfTransport, float]],
            unit: str
    ) -> plotly.graph_objects.Figure:

        vehicle_types = [str(vehicle_type).replace("_", " ") for vehicle_type in inbound_to_outbound_flow.keys()]
        source_ids = list(range(len(vehicle_types)))
        target_ids = list(range(len(vehicle_types), 2 * len(vehicle_types)))
        value_ids = list(itertools.product(source_ids, target_ids))
        source_ids_with_duplication = [source_id for (source_id, _) in value_ids]
        target_ids_with_duplication = [target_id for (_, target_id) in value_ids]
        value = [
            inbound_to_outbound_flow[inbound_vehicle_type][outbound_vehicle_type]
            for inbound_vehicle_type in inbound_to_outbound_flow.keys()
            for outbound_vehicle_type in inbound_to_outbound_flow[inbound_vehicle_type].keys()
        ]
        if sum(value) == 0:
            self.logger.warning("No data available for plotting")
        inbound_labels = [
            str(inbound_vehicle_type).replace("_", " ").capitalize() + " inbound:<br>" + str(
                round(sum(inbound_to_outbound_flow[inbound_vehicle_type].values()), 2)) + " " + unit
            for inbound_vehicle_type in inbound_to_outbound_flow.keys()
        ]
        to_outbound_flow = [0 for _ in range(len(inbound_to_outbound_flow.keys()))]
        for inbound_vehicle_type, inbound_capacity in inbound_to_outbound_flow.items():
            for i, outbound_vehicle_type in enumerate(inbound_to_outbound_flow[inbound_vehicle_type].keys()):
                to_outbound_flow[i] += inbound_capacity[outbound_vehicle_type]
        outbound_labels = [
            str(outbound_vehicle_type).replace("_", " ").capitalize() + " outbound:<br>" + str(
                round(to_outbound_flow[i], 2)) + " " + unit
            for i, outbound_vehicle_type in enumerate(inbound_to_outbound_flow.keys())
        ]
        fig = plotly.graph_objects.Figure(
            data=[
                plotly.graph_objects.Sankey(
                    arrangement='perpendicular',
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(
                            color="black",
                            width=0.5
                        ),
                        label=inbound_labels + outbound_labels,
                        color="dimgray",
                    ),
                    link=dict(
                        source=source_ids_with_duplication,
                        target=target_ids_with_duplication,
                        value=value
                    )
                )
            ]
        )
        plot_title = "Container flow from vehicle type A to B as defined by generated containers " \
                     f"(in {unit})"
        fig.update_layout(
            title_text=plot_title,
            font_size=10,
            width=900,
            height=700
        )
        return fig
