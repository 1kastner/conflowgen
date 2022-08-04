from __future__ import annotations

from typing import Dict

from conflowgen.previews.modal_split_preview import ModalSplitPreview
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.reporting import AbstractReportWithMatplotlib, modal_split_report
from conflowgen.reporting.modal_split_report import plot_modal_splits


class ModalSplitPreviewReport(AbstractReportWithMatplotlib):
    """
    This preview report takes the data structure as generated by
    :class:`.ModalSplitPreview`
    and creates a comprehensible representation for the user, either as text or as a graph.
    The visual and table are expected to approximately look like in the
    `example ModalSplitPreviewReport <notebooks/previews.ipynb#Modal-Split-Preview-Report>`_.
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
            self, **kwargs
    ) -> str:
        assert len(kwargs) == 0, f"No keyword arguments supported for {self.__class__.__name__}"

        preview = self._get_updated_preview()

        # gather data
        transshipment_and_hinterland_split = preview.get_transshipment_and_hinterland_split()

        modal_split_in_hinterland_inbound_traffic = preview.get_modal_split_for_hinterland(
            inbound=True, outbound=False
        )

        modal_split_in_hinterland_outbound_traffic = preview.get_modal_split_for_hinterland(
            inbound=False, outbound=True
        )

        modal_split_in_hinterland_traffic_both_directions = preview.get_modal_split_for_hinterland(
            inbound=True, outbound=True
        )

        report = modal_split_report.insert_values_in_template(
            transshipment_and_hinterland_split=transshipment_and_hinterland_split,
            modal_split_in_hinterland_inbound_traffic=modal_split_in_hinterland_inbound_traffic,
            modal_split_in_hinterland_outbound_traffic=modal_split_in_hinterland_outbound_traffic,
            modal_split_in_hinterland_traffic_both_directions=modal_split_in_hinterland_traffic_both_directions
        )

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

    def get_report_as_graph(self, **kwargs) -> object:
        """
        The report as a graph is represented as a set of pie charts using pandas.

        Returns:
             The matplotlib axes
        """
        assert len(kwargs) == 0, f"No keyword arguments supported for {self.__class__.__name__}"

        preview = self._get_updated_preview()

        # gather data
        transshipment_and_hinterland_split = preview.get_transshipment_and_hinterland_split()
        modal_split_in_hinterland_inbound_traffic = preview.get_modal_split_for_hinterland(
            inbound=True, outbound=False
        )
        modal_split_in_hinterland_outbound_traffic = preview.get_modal_split_for_hinterland(
            inbound=False, outbound=True
        )
        modal_split_in_hinterland_traffic_both_directions = preview.get_modal_split_for_hinterland(
            inbound=True, outbound=True
        )

        axes = plot_modal_splits(
            transshipment_and_hinterland_split=transshipment_and_hinterland_split,
            modal_split_in_hinterland_both_directions=modal_split_in_hinterland_traffic_both_directions,
            modal_split_in_hinterland_inbound_traffic=modal_split_in_hinterland_inbound_traffic,
            modal_split_in_hinterland_outbound_traffic=modal_split_in_hinterland_outbound_traffic,
        )

        return axes
