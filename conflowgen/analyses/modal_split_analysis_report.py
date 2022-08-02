from __future__ import annotations

import numpy as np
import seaborn as sns

from conflowgen.analyses.modal_split_analysis import ModalSplitAnalysis
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.modal_split_report import plot_modal_splits

sns.set_palette(sns.color_palette())


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
            self
    ) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.
        """

        # gather data
        transshipment = self.analysis.get_transshipment_and_hinterland_split()
        transshipment_as_fraction = np.nan
        if sum(transshipment) > 0:
            transshipment_as_fraction = (
                    transshipment.transshipment_capacity /
                    (transshipment.transshipment_capacity + transshipment.hinterland_capacity)
            )
        modal_split_for_hinterland_inbound = self.analysis.get_modal_split_for_hinterland(
            inbound=True, outbound=False
        )
        inbound_total = sum(modal_split_for_hinterland_inbound)
        if inbound_total == 0:
            inbound_total = np.nan
        modal_split_for_hinterland_outbound = self.analysis.get_modal_split_for_hinterland(
            inbound=False, outbound=True
        )
        outbound_total = sum(modal_split_for_hinterland_outbound)
        if outbound_total == 0:
            outbound_total = np.nan
        modal_split_for_hinterland_both = self.analysis.get_modal_split_for_hinterland(
            inbound=True, outbound=True
        )
        inbound_and_outbound_total = sum(modal_split_for_hinterland_both)
        if inbound_and_outbound_total == 0:
            inbound_and_outbound_total = np.nan

        # create string representation
        report = "\nTransshipment share\n"
        report += f"transshipment proportion (in TEU): {transshipment.transshipment_capacity:>10.2f} "
        report += f"({transshipment_as_fraction * 100:.2f}%)\n"
        report += f"hinterland proportion (in TEU):    {transshipment.hinterland_capacity:>10.2f} "
        report += f"({(1 - transshipment_as_fraction) * 100:.2f}%)\n"
        report += "\n"

        report += "Inbound modal split\n"
        report += f"truck proportion (in TEU): {modal_split_for_hinterland_inbound.truck_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_inbound.truck_capacity / inbound_total * 100:.2f}%)\n"
        report += f"barge proportion (in TEU): {modal_split_for_hinterland_inbound.barge_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_inbound.barge_capacity / inbound_total * 100:.2f}%)\n"
        report += f"train proportion (in TEU): {modal_split_for_hinterland_inbound.train_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_inbound.train_capacity / inbound_total * 100:.2f}%)\n\n"

        report += "Outbound modal split\n"
        report += f"truck proportion (in TEU): {modal_split_for_hinterland_outbound.truck_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_outbound.truck_capacity / outbound_total * 100:.2f}%)\n"
        report += f"barge proportion (in TEU): {modal_split_for_hinterland_outbound.barge_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_outbound.barge_capacity / outbound_total * 100:.2f}%)\n"
        report += f"train proportion (in TEU): {modal_split_for_hinterland_outbound.train_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_outbound.train_capacity / outbound_total * 100:.2f}%)\n\n"

        report += "Absolute modal split (both inbound and outbound)\n"
        report += f"truck proportion (in TEU): {modal_split_for_hinterland_both.truck_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_both.truck_capacity / inbound_and_outbound_total * 100:.2f}%)\n"
        report += f"barge proportion (in TEU): {modal_split_for_hinterland_both.barge_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_both.barge_capacity / inbound_and_outbound_total * 100:.2f}%)\n"
        report += f"train proportion (in TEU): {modal_split_for_hinterland_both.train_capacity:>10.1f} "
        report += f"({modal_split_for_hinterland_both.train_capacity / inbound_and_outbound_total * 100:.2f}%)\n"

        report = report.replace("(nan%)", "(-%)")

        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self) -> object:
        """
        The report as a graph is represented as a set of pie charts using pandas.

        Returns:
             The matplotlib axis of the last bar chart.
        """

        # gather data
        transshipment_and_hinterland_split = self.analysis.get_transshipment_and_hinterland_split()
        modal_split_for_hinterland_inbound = self.analysis.get_modal_split_for_hinterland(
            inbound=True, outbound=False
        )
        modal_split_for_hinterland_outbound = self.analysis.get_modal_split_for_hinterland(
            inbound=False, outbound=True
        )
        modal_split_for_hinterland_both = self.analysis.get_modal_split_for_hinterland(
            inbound=True, outbound=True
        )

        axes = plot_modal_splits(
            transshipment_and_hinterland_split=transshipment_and_hinterland_split,
            modal_split_for_hinterland_both=modal_split_for_hinterland_both,
            modal_split_for_hinterland_inbound=modal_split_for_hinterland_inbound,
            modal_split_for_hinterland_outbound=modal_split_for_hinterland_outbound,
        )

        return axes
