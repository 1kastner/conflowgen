from __future__ import annotations

from typing import Dict

import numpy as np

from conflowgen.previews.abstract_preview_report import AbstractPreviewReportWithMatplotlib
from conflowgen.previews.modal_split_preview import ModalSplitPreview
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class ModalSplitPreviewReport(AbstractPreviewReportWithMatplotlib):
    """
    This preview report takes the data structure as generated by
    :class:`.ModalSplitPreview`
    and creates a comprehensible representation for the user, either as text or as a graph.
    The visual and table are expected to approximately look like in the
    `example ModalSplitPreviewReport <notebooks/previews.ipynb#ModalSplitPreviewReport>`_.
    """

    report_description = """
    This report previews the container flow in terms of transshipment share and modal split for the hinterland.
    The reported statistics of the hinterland are separated into three groups:
    The containers that have been delivered to the container terminal on the inbound journey of a vehicle,
    the containers that have been picked up from the container terminal on the outbound journey of a vehicle,
    and the combination of both of them.
    """

    def __init__(self):
        super().__init__()
        self.preview = ModalSplitPreview(
            start_date=self.start_date,
            end_date=self.end_date,
            transportation_buffer=self.transportation_buffer
        )

    def hypothesize_with_mode_of_transport_distribution(
            self,
            mode_of_transport_distribution: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
    ):
        self.preview.hypothesize_with_mode_of_transport_distribution(mode_of_transport_distribution)

    def get_report_as_text(
            self
    ) -> str:
        preview = self._get_updated_preview()

        # gather data
        transshipment = preview.get_transshipment_and_hinterland_share()
        transshipment_as_fraction = np.nan
        if sum(transshipment) > 0:
            transshipment_as_fraction = (
                transshipment.transshipment_capacity /
                (transshipment.transshipment_capacity + transshipment.hinterland_capacity)
            )
        modal_split_for_hinterland_inbound = preview.get_modal_split_for_hinterland(
            inbound=True, outbound=False
        )
        inbound_total = sum(modal_split_for_hinterland_inbound)
        if inbound_total == 0:
            inbound_total = np.nan
        modal_split_for_hinterland_outbound = preview.get_modal_split_for_hinterland(
            inbound=False, outbound=True
        )
        outbound_total = sum(modal_split_for_hinterland_outbound)
        if outbound_total == 0:
            outbound_total = np.nan
        modal_split_for_hinterland_both = preview.get_modal_split_for_hinterland(
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

    def _get_updated_preview(self) -> ModalSplitPreview:
        assert self.start_date is not None
        assert self.end_date is not None
        assert self.transportation_buffer is not None
        self.preview.update(
            start_date=self.start_date,
            end_date=self.end_date,
            transportation_buffer=self.transportation_buffer
        )
        return self.preview

    def get_report_as_graph(self) -> object:
        """
        The report as a graph is represented as a set of pie charts using pandas.

        Returns: The matplotlib axis of the last bar chart.

        .. todo:: All pie charts should be plotted in a single plot using subplots.
        """
        preview = self._get_updated_preview()
        import pandas as pd  # pylint: disable=import-outside-toplevel
        import matplotlib.pyplot as plt  # pylint: disable=import-outside-toplevel
        import seaborn as sns  # pylint: disable=import-outside-toplevel

        sns.set_palette(sns.color_palette())

        # gather data
        transshipment = preview.get_transshipment_and_hinterland_share()
        modal_split_for_hinterland_inbound = preview.get_modal_split_for_hinterland(
            inbound=True, outbound=False
        )
        modal_split_for_hinterland_outbound = preview.get_modal_split_for_hinterland(
            inbound=False, outbound=True
        )
        modal_split_for_hinterland_both = preview.get_modal_split_for_hinterland(
            inbound=True, outbound=True
        )

        # Start plotting
        series_hinterland_and_transshipment = pd.Series({
            "hinterland capacity": transshipment.hinterland_capacity,
            "transshipment capacity": transshipment.transshipment_capacity
        }, name="Transshipment share")
        series_hinterland_and_transshipment.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title="Transshipment share"
        )
        plt.show()

        series_modal_split_inbound = pd.Series({
            "train": modal_split_for_hinterland_inbound.train_capacity,
            "truck": modal_split_for_hinterland_inbound.truck_capacity,
            "barge": modal_split_for_hinterland_inbound.barge_capacity
        }, name="Modal split for hinterland (inbound)")
        series_modal_split_inbound.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title="Modal split for hinterland (inbound)"
        )
        plt.show()

        series_modal_split_outbound = pd.Series({
            "train": modal_split_for_hinterland_outbound.train_capacity,
            "truck": modal_split_for_hinterland_outbound.truck_capacity,
            "barge": modal_split_for_hinterland_outbound.barge_capacity
        }, name="Modal split for hinterland (outbound)")
        series_modal_split_outbound.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title="Modal split for hinterland (outbound)"
        )
        plt.show()

        series_modal_split_both = pd.Series({
            "train": modal_split_for_hinterland_both.train_capacity,
            "truck": modal_split_for_hinterland_both.truck_capacity,
            "barge": modal_split_for_hinterland_both.barge_capacity
        }, name="Modal split for hinterland (inbound and outbound)")
        ax = series_modal_split_both.plot.pie(
            legend=False,
            autopct='%1.1f%%',
            label="",
            title="Modal split for hinterland (inbound and outbound)"
        )
        plt.show()

        return ax
