from __future__ import annotations

from typing import Dict

import pandas as pd

from conflowgen.descriptive_datatypes import InboundAndOutboundContainerVolume
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.previews.quay_side_throughput_preview import QuaySideThroughputPreview
from conflowgen.reporting import AbstractReportWithMatplotlib


class QuaySideThroughputPreviewReport(AbstractReportWithMatplotlib):
    """
    This preview report takes the data structure as generated by
    :class:`.QuaySideThroughputPreview`
    and creates a comprehensible representation for the user, either as text or as a graph.
    """

    report_description = """
    This report previews the inbound and outbound traffic at the quay side. 
    This is only an estimate, additional restrictions (such as the dwell time restrictions) might further
    reduce the number of containers one vehicle can in fact pick up for its outbound journey.
    """

    def __init__(self):
        super().__init__()
        self._df = None
        self.preview = QuaySideThroughputPreview(
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
            self, **kwargs
    ) -> str:
        assert len(kwargs) == 0, f"No keyword arguments supported for {self.__class__.__name__}"

        quay_side_throughput = self._get_quay_side_throughput()

        # create string representation
        report = "\n"
        report += "discharged (in containers) "
        report += "loaded (in containers)"
        report += "\n"

        report += f"{int(round(quay_side_throughput.inbound.containers)):>26} "
        report += f"{int(round(quay_side_throughput.outbound.containers)):>22}"
        report += "\n"

        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self, **kwargs) -> object:
        assert len(kwargs) == 0, f"No keyword arguments supported for {self.__class__.__name__}"

        quay_side_throughput = self._get_quay_side_throughput()

        series = pd.Series({
            "Number discharged containers": quay_side_throughput.inbound.containers,
            "Number loaded containers": quay_side_throughput.outbound.containers
        }, name="Quayside Throughput")

        ax = series.plot()

        return ax

    def _get_quay_side_throughput(self) -> InboundAndOutboundContainerVolume:
        assert self.start_date is not None
        assert self.end_date is not None
        assert self.transportation_buffer is not None
        self.preview.update(
            start_date=self.start_date,
            end_date=self.end_date,
            transportation_buffer=self.transportation_buffer
        )
        # gather data
        quay_side_throughput = self.preview.get_quay_side_throughput()
        return quay_side_throughput
