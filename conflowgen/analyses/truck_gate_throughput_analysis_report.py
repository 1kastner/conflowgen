from __future__ import annotations

import statistics
import pandas as pd
import matplotlib.pyplot as plt

from conflowgen.analyses.truck_gate_throughput_analysis import TruckGateThroughputAnalysis
from conflowgen.reporting import AbstractReportWithMatplotlib
from conflowgen.reporting.no_data_plot import no_data_graph


class TruckGateThroughputAnalysisReport(AbstractReportWithMatplotlib):
    """
    This analysis report takes the data structure as generated by :class:`.TruckGateThroughputAnalysis`
    and creates a comprehensible representation for the user, either as text or as a graph.
    """

    report_description = """
    Analyze the trucks entering through the truck gate at each hour. Based on this, the required truck gate capacity in
    containers boxes can be deduced.
    In the text version of the report, only the statistics are reported.
    In the visual version of the report, the time series is plotted.
    """

    def __init__(self):
        super().__init__()
        self.analysis = TruckGateThroughputAnalysis()

    def get_report_as_text(self, **kwargs) -> str:
        assert len(kwargs) == 0, f"No keyword arguments supported for {self.__class__.__name__}"

        truck_gate_throughput = self.analysis.get_throughput_over_time()
        if truck_gate_throughput:
            truck_gate_throughput_sequence = list(truck_gate_throughput.values())
            maximum_truck_gate_throughput = max(truck_gate_throughput_sequence)
            average_truck_gate_throughput = statistics.mean(truck_gate_throughput_sequence)
            stddev_truck_gate_throughput = statistics.stdev(truck_gate_throughput_sequence)
        else:
            maximum_truck_gate_throughput = average_truck_gate_throughput = 0
            stddev_truck_gate_throughput = -1

        # create string representation
        report = "\n"
        report += "                                     (reported in boxes)\n"
        report += f"maximum hourly truck gate throughput:         {maximum_truck_gate_throughput:>10}\n"
        report += f"average hourly truck gate throughput:         {average_truck_gate_throughput:>10.1f}\n"
        report += f"standard deviation:                           {stddev_truck_gate_throughput:>10.1f}\n"
        report += "(rounding errors might exist)\n"

        return report

    def get_report_as_graph(self, **kwargs) -> object:
        """
        The report as a graph is represented as a line graph using pandas.

        Returns:
             The matplotlib axis of the bar chart.
        """
        assert len(kwargs) == 0, f"No keyword arguments supported for {self.__class__.__name__}"

        truck_gate_throughput = self.analysis.get_throughput_over_time()
        if len(truck_gate_throughput) == 0:
            return no_data_graph()

        series = pd.Series(truck_gate_throughput)
        ax = series.plot()
        plt.xticks(rotation=45)
        ax.set_xlabel("Date")
        ax.set_ylabel("Number of boxes (hourly count)")
        ax.set_title("Analysis of truck gate throughput")
        return ax
