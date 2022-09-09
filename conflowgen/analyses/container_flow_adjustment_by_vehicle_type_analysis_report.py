from __future__ import annotations

import itertools
import logging

import plotly.graph_objs

from conflowgen.analyses.container_flow_adjustment_by_vehicle_type_analysis import \
    ContainerFlowAdjustmentByVehicleTypeAnalysis
from conflowgen.reporting import AbstractReportWithPlotly


class ContainerFlowAdjustmentByVehicleTypeAnalysisReport(AbstractReportWithPlotly):
    """
    This analysis report takes the data structure as generated by
    :class:`.ContainerFlowAdjustmentByVehicleTypeAnalysis` and creates a comprehensible representation for the
    user, either as text or as a graph.
    """

    report_description = """
    Analyze how many containers needed to change their initial container type.
    When containers are generated, in order to obey the maximum dwell time, the vehicle type that is used for
    onward transportation might change. The initial outbound vehicle type is the vehicle type that is drawn
    randomly for a container at the time of generation. The adjusted vehicle type is the vehicle type that is drawn
    in case no vehicle of the initial outbound vehicle type is left within the maximum dwell time.
    """

    logger = logging.getLogger("conflowgen")

    def __init__(self):
        super().__init__()
        self.analysis = ContainerFlowAdjustmentByVehicleTypeAnalysis()

    def get_report_as_text(
            self, **kwargs
    ) -> str:
        assert len(kwargs) == 0, f"No keyword arguments supported for {self.__class__.__name__}"

        initial_to_adjusted_outbound_flow = self.analysis.get_initial_to_adjusted_outbound_flow()
        initial_to_adjusted_outbound_flow_in_containers = initial_to_adjusted_outbound_flow.containers
        initial_to_adjusted_outbound_flow_in_teu = initial_to_adjusted_outbound_flow.teu

        # create string representation
        report = "\n"
        report += "initial vehicle type  "
        report += "adjusted vehicle type  "
        report += "transported capacity (in TEU) "
        report += "transported capacity (in boxes)"
        report += "\n"
        for vehicle_type_initial, vehicle_type_adjusted in itertools.product(
                self.order_of_vehicle_types_in_report, repeat=2):
            vehicle_type_from_as_text = str(vehicle_type_initial).replace("_", " ")
            vehicle_type_to_as_text = str(vehicle_type_adjusted).replace("_", " ")
            transported_capacity_in_teu = initial_to_adjusted_outbound_flow_in_teu[vehicle_type_initial][
                vehicle_type_adjusted]
            transported_capacity_in_containers = initial_to_adjusted_outbound_flow_in_containers[vehicle_type_initial][
                vehicle_type_adjusted]
            report += f"{vehicle_type_from_as_text:<21} "
            report += f"{vehicle_type_to_as_text:<23} "
            report += f"{transported_capacity_in_teu:>28.1f}"
            report += f"{transported_capacity_in_containers:>32}"
            report += "\n"

        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self, **kwargs) -> plotly.graph_objs.Figure:
        """
        The container flow is represented by a Sankey diagram.

        .. note::
            At the time of writing, plotly comes with some shortcomings.

            * Sorting the labels on either the left or right side without recalculating the height of each bar is not
              possible, see https://github.com/plotly/plotly.py/issues/1732.
            * Empty nodes require special handling, see https://github.com/plotly/plotly.py/issues/3003 and the
              coordinates need to be :math:`0 < x,y < 1` (no equals!), see
              https://github.com/plotly/plotly.py/issues/3002.

            However, it seems to be the best available library for plotting Sankey diagrams that can be visualized,
            e.g., in a Jupyter Notebook.

        Returns:
            The plotly figure of the Sankey diagram.
        """
        assert len(kwargs) == 0, f"The following keys have not been processed: {list(kwargs.keys())}"

        unit = "TEU"

        initial_to_adjusted_outbound_flow = self.analysis.get_initial_to_adjusted_outbound_flow()
        initial_to_adjusted_outbound_flow_in_teu = initial_to_adjusted_outbound_flow.teu

        vehicle_types = [
            str(vehicle_type).replace("_", " ")
            for vehicle_type in initial_to_adjusted_outbound_flow_in_teu.keys()
        ]
        source_ids = list(range(len(vehicle_types)))
        target_ids = list(range(len(vehicle_types), 2 * len(vehicle_types)))
        value_ids = list(itertools.product(source_ids, target_ids))
        source_ids_with_duplication = [source_id for (source_id, _) in value_ids]
        target_ids_with_duplication = [target_id for (_, target_id) in value_ids]
        value = [
            initial_to_adjusted_outbound_flow_in_teu[vehicle_type_initial][vehicle_type_adjusted]
            for vehicle_type_initial in initial_to_adjusted_outbound_flow_in_teu.keys()
            for vehicle_type_adjusted in initial_to_adjusted_outbound_flow_in_teu[vehicle_type_initial].keys()
        ]

        if sum(value) == 0:
            self.logger.warning("No data available for plotting")

        initial_labels = [
            str(vehicle_type_initial).replace("_", " ").capitalize() + " initial:<br>" + str(
                round(sum(initial_to_adjusted_outbound_flow_in_teu[vehicle_type_initial].values()), 2)
            ) + " " + unit
            for vehicle_type_initial in initial_to_adjusted_outbound_flow_in_teu.keys()
        ]
        to_adjusted_flow = [0 for _ in range(len(initial_to_adjusted_outbound_flow_in_teu.keys()))]
        for vehicle_type_initial, capacity in initial_to_adjusted_outbound_flow_in_teu.items():
            for i, vehicle_type_adjusted in enumerate(initial_to_adjusted_outbound_flow_in_teu[vehicle_type_initial]):
                to_adjusted_flow[i] += capacity[vehicle_type_adjusted]
        adjusted_labels = [
            str(vehicle_type_adjusted).replace("_", " ").capitalize() + " adjusted:<br> " + str(
                round(to_adjusted_flow[i], 2)) + " " + unit
            for i, vehicle_type_adjusted in enumerate(initial_to_adjusted_outbound_flow_in_teu.keys())
        ]
        fig = plotly.graph_objs.Figure(
            data=[
                plotly.graph_objs.Sankey(
                    arrangement='perpendicular',
                    node=dict(
                        pad=15,
                        thickness=20,
                        line=dict(
                            color="black",
                            width=0.5
                        ),
                        label=initial_labels + adjusted_labels,
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

        fig.update_layout(
            title_text=f"Container flow from initial vehicle type A to adjusted vehicle type B in {unit} as for some "
                       "containers<br>"
                       "the initially intended vehicle type was not available due to constraints "
                       "(schedules, dwell times, etc.).",
            font_size=10,
            width=900,
            height=700
        )
        return fig
