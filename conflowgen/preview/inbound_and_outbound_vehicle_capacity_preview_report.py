from __future__ import annotations

from typing import Dict

from conflowgen.preview.abstract_review_report import AbstractPreviewReport
from conflowgen.preview.inbound_and_outbound_vehicle_capacity_preview import \
    InboundAndOutboundVehicleCapacityPreview
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class InboundAndOutboundVehicleCapacityPreviewReport(AbstractPreviewReport):
    """
    This preview report takes the data structure as generated by
    :class:`.InboundAndOutboundVehicleCapacityPreview` and creates a comprehensible representation for the
    user, either as text or as a graph.
    """

    def __init__(self):
        super().__init__()
        self.preview = InboundAndOutboundVehicleCapacityPreview(
            self.start_date,
            self.end_date,
            self.transportation_buffer
        )

    def hypothesize_with_mode_of_transport_distribution(
            self,
            mode_of_transport_distribution: Dict[ModeOfTransport, Dict[ModeOfTransport, float]]
    ):
        self.preview.hypothesize_with_mode_of_transport_distribution(mode_of_transport_distribution)

    def get_report_as_text(self) -> str:
        inbound_capacities, outbound_average_capacities, outbound_maximum_capacities = self._get_capacities()

        # create string representation
        report = "\n"
        report += "vehicle type    "
        report += "inbound capacity "
        report += "outbound avg capacity "
        report += "outbound max capacity"
        report += "\n"
        for vehicle_type in self.order_of_vehicle_types_in_report:
            vehicle_type_as_text = str(vehicle_type).replace("_", " ")
            report += f"{vehicle_type_as_text:<15} "
            report += f"{inbound_capacities[vehicle_type]:>16.1f} "
            report += f"{outbound_average_capacities[vehicle_type]:>21.1f} "
            report += f"{outbound_maximum_capacities[vehicle_type]:>21.1f}"
            report += "\n"
        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self) -> object:
        """
        The report as a graph is represented as a bar chart using pandas.

        Returns: The matplotlib axis of the bar chart.
        """
        import pandas as pd  # pylint: disable=import-outside-toplevel
        import seaborn as sns  # pylint: disable=import-outside-toplevel
        sns.set_palette(sns.color_palette())

        inbound_capacities, outbound_average_capacities, outbound_maximum_capacities = self._get_capacities()
        df = pd.DataFrame({
            "inbound capacities": inbound_capacities,
            "outbound average capacities": outbound_average_capacities,
            "outbound maximum capacities": outbound_maximum_capacities
        })
        df.index = [str(i).replace("_", " ") for i in df.index]
        ax = df.plot.barh()
        ax.set_xlabel("Capacity (in TEU)")
        ax.set_title("Inbound and outbound vehicle capacity preview")
        return ax

    def _get_capacities(self):
        assert self.start_date is not None
        assert self.end_date is not None
        assert self.transportation_buffer is not None
        self.preview.update(
            start_date=self.start_date,
            end_date=self.end_date,
            transportation_buffer=self.transportation_buffer
        )
        # gather data
        inbound_capacities = self.preview.get_inbound_capacity_of_vehicles()
        outbound_average_capacities, outbound_maximum_capacities = self.preview.get_outbound_capacity_of_vehicles()
        return inbound_capacities, outbound_average_capacities, outbound_maximum_capacities
