from __future__ import annotations

import typing  # noqa, pylint: disable=unused-import  # lgtm [py/unused-import]  # used in the docstring
import matplotlib.axes

from conflowgen.analyses.modal_split_analysis import ModalSplitAnalysis
from conflowgen.reporting import AbstractReportWithMatplotlib, modal_split_report
from conflowgen.reporting.modal_split_report import plot_modal_splits


class ModalSplitAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.ModalSplitAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    """

    report_description = """
    Analyze the amount of containers dedicated for or coming from the hinterland compared to the amount of containers
    that are transshipment.
    """

    def __init__(self):
        super().__init__()
        self.analysis = ModalSplitAnalysis()

    def get_report_as_text(
            self, **kwargs
    ) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.

        Keyword Args:
            start_time (typing.Optional[datetime.datetime]):
                Only include containers that arrive after the given start time.
            end_time (typing.Optional[datetime.datetime]):
                Only include containers that depart before the given end time.
        """
        (
            modal_split_in_hinterland_traffic_both_directions, modal_split_in_hinterland_inbound_traffic,
            modal_split_in_hinterland_outbound_traffic,  transshipment_and_hinterland_split
        ) = self._get_analysis_output(kwargs)

        report = modal_split_report.insert_values_in_template(
            transshipment_and_hinterland_split=transshipment_and_hinterland_split,
            modal_split_in_hinterland_inbound_traffic=modal_split_in_hinterland_inbound_traffic,
            modal_split_in_hinterland_outbound_traffic=modal_split_in_hinterland_outbound_traffic,
            modal_split_in_hinterland_traffic_both_directions=modal_split_in_hinterland_traffic_both_directions
        )

        return report

    def get_report_as_graph(self, **kwargs) -> matplotlib.axes.Axes:
        """
        The report as a graph is represented as a set of pie charts using pandas.

        Keyword Args:
            start_time (typing.Optional[datetime.datetime]):
                Only include containers that arrive after the given start time.
            end_time (typing.Optional[datetime.datetime]):
                Only include containers that depart before the given end time.

        Returns:
             The matplotlib axes with all pie charts.
        """
        (
            modal_split_in_hinterland_traffic_both_directions, modal_split_in_hinterland_inbound_traffic,
            modal_split_in_hinterland_outbound_traffic, transshipment_and_hinterland_split
        ) = self._get_analysis_output(kwargs)

        axes = plot_modal_splits(
            transshipment_and_hinterland_split=transshipment_and_hinterland_split,
            modal_split_in_hinterland_both_directions=modal_split_in_hinterland_traffic_both_directions,
            modal_split_in_hinterland_inbound_traffic=modal_split_in_hinterland_inbound_traffic,
            modal_split_in_hinterland_outbound_traffic=modal_split_in_hinterland_outbound_traffic,
        )

        return axes

    def _get_analysis_output(self, kwargs):
        start_time = kwargs.pop("start_time", None)
        end_time = kwargs.pop("end_time", None)
        assert len(kwargs) == 0, f"Keyword(s) {kwargs.keys()} have not been processed"

        transshipment_and_hinterland_split = self.analysis.get_transshipment_and_hinterland_split(
            start_time=start_time, end_time=end_time
        )
        modal_split_in_hinterland_inbound_traffic = self.analysis.get_modal_split_for_hinterland_traffic(
            inbound=True, outbound=False, start_time=start_time, end_time=end_time
        )
        modal_split_in_hinterland_outbound_traffic = self.analysis.get_modal_split_for_hinterland_traffic(
            inbound=False, outbound=True, start_time=start_time, end_time=end_time
        )
        modal_split_in_hinterland_traffic_both_directions = self.analysis.get_modal_split_for_hinterland_traffic(
            inbound=True, outbound=True, start_time=start_time, end_time=end_time
        )
        return (
            modal_split_in_hinterland_traffic_both_directions, modal_split_in_hinterland_inbound_traffic,
            modal_split_in_hinterland_outbound_traffic, transshipment_and_hinterland_split
        )
