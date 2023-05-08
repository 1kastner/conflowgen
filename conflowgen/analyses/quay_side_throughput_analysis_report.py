from __future__ import annotations

import statistics
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.axis

from conflowgen.analyses.quay_side_throughput_analysis import QuaySideThroughputAnalysis
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph


class QuaySideThroughputAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.QuaySideThroughputAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    The visual and table are expected to approximately look like in the
    `example QuaySideThroughputAnalysisReport \
    <notebooks/analyses.ipynb#Quay-Side-Throughput-Analysis-Report>`_.
    """

    report_description = """
    Analyse the throughput at the quay side.
    In the text version of the report, only the statistics are reported.
    In the visual version of the report, the time series is plotted.
    There is no concept of handling times in the data generation process (as this is the task of the simulation or
    optimization model using this data on a later stage) and thus all containers are loaded and discharged at once.
    The impact of this fact is mitigated by averaging the data over certain time ranges.
    """

    plot_title = "Analysis of quay side throughput"

    def __init__(self):
        super().__init__()
        self.analysis = QuaySideThroughputAnalysis()

    def get_report_as_text(self, **kwargs) -> str:
        quay_side_throughput = self._get_analysis_result(kwargs)
        assert len(kwargs) == 0, f"Keyword(s) {list(kwargs.keys())} have not been processed."

        if quay_side_throughput:
            quay_side_throughput_sequence = list(quay_side_throughput.values())
            maximum_quay_side_throughput = max(quay_side_throughput_sequence)
            average_quay_side_throughput = statistics.mean(quay_side_throughput_sequence)
            stddev_quay_side_throughput = statistics.stdev(quay_side_throughput_sequence)
        else:
            maximum_quay_side_throughput = average_quay_side_throughput = 0
            stddev_quay_side_throughput = -1

        # create string representation
        report = "\n"
        report += "                                     (reported in boxes)\n"
        report += f"maximum weekly quay side throughput:          {maximum_quay_side_throughput:>10}\n"
        report += f"average weekly quay side throughput:          {average_quay_side_throughput:>10.1f}\n"
        report += f"standard deviation:                           {stddev_quay_side_throughput:>10.1f}\n"
        report += f"maximum daily quay side throughput:           {(maximum_quay_side_throughput / 7):>10.1f}\n"
        report += f"average daily quay side throughput:           {(average_quay_side_throughput / 7):>10.1f}\n"
        report += f"maximum hourly quay side throughput:          {(maximum_quay_side_throughput / 168):>10.1f}\n"
        report += f"average hourly quay side throughput:          {(average_quay_side_throughput / 168):>10.1f}\n"
        report += "(daily and hourly values are simply scaled weekly values, rounding errors might exist)\n"

        return report

    def get_report_as_graph(self, **kwargs) -> matplotlib.axis.Axis:
        """
        The report as a graph is represented as a line graph using pandas.

        Keyword Args:
            start_date (datetime.datetime):
                Only include containers that arrive after the given start time.
            end_date (datetime.datetime):
                Only include containers that depart before the given end time.
            use_cache (bool):


        Returns:
             The matplotlib axis of the line chart over time.
        """
        quay_side_throughput = self._get_analysis_result(kwargs)
        assert len(kwargs) == 0, f"Keyword(s) {list(kwargs.keys())} have not been processed."

        if len(quay_side_throughput) == 0:
            fig, ax = no_data_graph()
        else:
            series = pd.Series(quay_side_throughput)
            ax = series.plot()
            plt.xticks(rotation=45)
            ax.set_xlabel("Date")
            ax.set_ylabel("Number of boxes (weekly count)")
        ax.set_title(self.plot_title)
        return ax

    def _get_analysis_result(self, kwargs):
        start_date = kwargs.pop("start_date", None)
        end_date = kwargs.pop("end_date", None)
        quay_side_throughput = self.analysis.get_throughput_over_time(
            start_date=start_date,
            end_date=end_date
        )
        return quay_side_throughput
