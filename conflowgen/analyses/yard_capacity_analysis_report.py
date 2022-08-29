from __future__ import annotations

import datetime
import statistics
from typing import Tuple, Any, Dict
import pandas as pd
import matplotlib.axis

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.analyses.yard_capacity_analysis import YardCapacityAnalysis
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph


class YardCapacityAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.YardCapacityAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    """

    report_description = """
    Analyse the used capacity in the yard.
    For each hour, the containers entering and leaving the yard are checked.
    Based on this, the required yard capacity in TEU can be deduced.
    In the text version of the report, only the statistics are reported.
    In the visual version of the report, the time series is plotted.
    There is no concept of handling times in the data generation process (as this is the task of the simulation or
    optimization model using this data on a later stage) and thus all containers are loaded and discharged at once.
    Thus, the yard utilization shows certain peaks that will most likely not occur, especially if the discharging and
    loading process of a vessel is parallelized.
    """

    def __init__(self):
        super().__init__()
        self.analysis = YardCapacityAnalysis()

    def get_report_as_text(self, **kwargs) -> str:
        """
        The report as a text is represented as a table suitable for logging. It uses a human-readable formatting style.

        Keyword Args:
            storage_requirement: Either a single storage requirement of type :class:`.StorageRequirement` or a whole
                collection of them, e.g., passed as a :class:`list` or :class:`set`.
                For the exact interpretation of the parameter, check
                :meth:`.YardCapacityAnalysis.get_used_yard_capacity_over_time`.

        Returns:
             The report in text format (possibly spanning over several lines).
        """

        storage_requirement, used_yard_capacity_over_time = \
            self._get_used_yard_capacity_based_on_storage_requirement(kwargs)

        if used_yard_capacity_over_time:
            used_yard_capacity_sequence = list(used_yard_capacity_over_time.values())
            maximum_used_yard_capacity = max(used_yard_capacity_sequence)
            average_used_yard_capacity = statistics.mean(used_yard_capacity_sequence)
            stddev_used_yard_capacity = statistics.stdev(used_yard_capacity_sequence)
        else:
            maximum_used_yard_capacity = average_used_yard_capacity = 0
            stddev_used_yard_capacity = -1

        used_laden_standard_container_yard_capacity_over_time = self.analysis.get_used_yard_capacity_over_time(
            storage_requirement=StorageRequirement.standard
        )
        if used_laden_standard_container_yard_capacity_over_time:
            used_laden_standard_yard_capacity_sequence = list(
                used_laden_standard_container_yard_capacity_over_time.values())
            maximum_used_laden_standard_yard_capacity = max(used_laden_standard_yard_capacity_sequence)
            average_used_laden_standard_yard_capacity = statistics.mean(used_laden_standard_yard_capacity_sequence)
            stddev_laden_standard_yard_capacity = statistics.stdev(
                used_laden_standard_yard_capacity_sequence)
        else:
            maximum_used_laden_standard_yard_capacity = average_used_laden_standard_yard_capacity = 0
            stddev_laden_standard_yard_capacity = -1

        # create string representation
        report = "\n"
        report += "storage requirement = " + self._get_storage_requirement_representation(storage_requirement) + "\n"
        report += "                                     (reported in TEU)\n"
        report += f"maximum used yard capacity:                 {maximum_used_yard_capacity:>10.1f}\n"
        report += f"average used yard capacity:                 {average_used_yard_capacity:>10.1f}\n"
        report += f"standard deviation:                         {stddev_used_yard_capacity:>10.1f}\n"
        report += f"maximum used yard capacity (laden):         {maximum_used_laden_standard_yard_capacity:>10.1f}\n"
        report += f"average used yard capacity (laden):         {average_used_laden_standard_yard_capacity:>10.1f}\n"
        report += f"standard deviation (laden):                 {stddev_laden_standard_yard_capacity:>10.1f}\n"
        report += "(rounding errors might exist)\n"
        return report

    def get_report_as_graph(self, **kwargs) -> matplotlib.axis.Axis:
        """
        The report as a graph is represented as a line graph using pandas.

        Keyword Args:
            storage_requirement: Either a single storage requirement of type :class:`.StorageRequirement` or a whole
                collection of them, e.g., passed as a :class:`list` or :class:`set`.
                For the exact interpretation of the parameter, check
                :meth:`.YardCapacityAnalysis.get_used_yard_capacity_over_time`.

        Returns:
             The matplotlib axis of the plot over time.
        """

        storage_requirement, yard_capacity_over_time = self._get_used_yard_capacity_based_on_storage_requirement(kwargs)

        if len(yard_capacity_over_time) == 0:
            ax = no_data_graph()
        else:
            series = pd.Series(yard_capacity_over_time)
            ax = series.plot()
        x_label = f"storage requirement = {self._get_storage_requirement_representation(storage_requirement)}"
        ax.set_xlabel(x_label)
        ax.set_ylabel("Used yard capacity (in TEU)")
        ax.set_title("Yard capacity analysis")
        return ax

    def _get_storage_requirement_representation(self, storage_requirement: Any) -> str:
        return self._get_enum_or_enum_set_representation(storage_requirement, StorageRequirement)

    def _get_used_yard_capacity_based_on_storage_requirement(
            self, kwargs
    ) -> Tuple[Any, Dict[datetime.datetime, float]]:
        storage_requirement = None
        if "storage_requirement" in kwargs:
            storage_requirement = kwargs["storage_requirement"]
            yard_capacity_over_time = self.analysis.get_used_yard_capacity_over_time(
                storage_requirement=storage_requirement
            )
        else:
            yard_capacity_over_time = self.analysis.get_used_yard_capacity_over_time()
        return storage_requirement, yard_capacity_over_time
