from __future__ import annotations

from typing import Dict

from conflowgen.preview.abstract_review_report import AbstractPreviewReport
from conflowgen.preview.vehicle_capacity_exceeded_preview import VehicleCapacityExceededPreview
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class VehicleCapacityExceededPreviewReport(AbstractPreviewReport):
    """
    This preview report takes the data structure as generated by
    :class:`.VehicleCapacityExceededPreview` and creates a comprehensible representation for the
    user, either as text or as a graph.
    """

    def __init__(self):
        super().__init__()
        self.preview = VehicleCapacityExceededPreview(
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
        comparison = self._get_comparison()

        # create string representation
        report = "\n"
        report += "vehicle type     "
        report += "maximum capacity (in TEU) "
        report += "required capacity (in TEU) "
        report += "exceeded "
        report += "difference (in TEU)"
        report += "\n"
        for vehicle_type in self.order_of_vehicle_types_in_report:
            vehicle_type_as_text = str(vehicle_type).replace("_", " ")
            report += f"{vehicle_type_as_text:<17} "

            (
                container_capacity_to_pick_up,
                maximum_capacity,
                vehicle_type_capacity_is_exceeded
            ) = comparison[vehicle_type]

            if not vehicle_type_capacity_is_exceeded:
                difference = 0
            else:
                difference = container_capacity_to_pick_up - maximum_capacity

            vehicle_type_capacity_is_exceeded_as_text = "yes" if vehicle_type_capacity_is_exceeded else "no"
            report += f"{maximum_capacity:>24.1f} "
            report += f"{container_capacity_to_pick_up:>25.1f} "
            report += f"{vehicle_type_capacity_is_exceeded_as_text:>9}"
            report += f"{difference:>20.1f}"
            report += "\n"

        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self) -> object:
        """

        Returns: The matplotlib axis of the bar chart.
        """
        comparison = self._get_comparison()
        import pandas as pd  # pylint: disable=import-outside-toplevel
        import seaborn as sns  # pylint: disable=import-outside-toplevel
        sns.set_palette(sns.color_palette())
        df = pd.DataFrame.from_dict(comparison).T
        df.columns = ["currently planned", "maximum", "exceeded"]
        df.index = [str(i).replace("_", " ") for i in df.index]
        df.rename({"truck": "truck (no max.)"}, axis=0, inplace=True)
        ax = df.plot.barh()
        ax.set_title("Capacity exceeded in preview?")
        ax.set_xlabel("Capacity (in TEU)")
        return ax

    def _get_comparison(self):
        assert self.start_date is not None
        assert self.end_date is not None
        assert self.transportation_buffer is not None
        self.preview.update(
            start_date=self.start_date,
            end_date=self.end_date,
            transportation_buffer=self.transportation_buffer
        )
        # gather data
        comparison = self.preview.compare()
        return comparison
