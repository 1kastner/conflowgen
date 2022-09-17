import datetime
import logging
import typing

from .container_dwell_time_analysis_report import ContainerDwellTimeAnalysisReport
from .container_flow_adjustment_by_vehicle_type_analysis_report import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisReport
from .container_flow_adjustment_by_vehicle_type_analysis_summary_report import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport
from .container_flow_by_vehicle_type_analysis_report import ContainerFlowByVehicleTypeAnalysisReport
from .container_flow_vehicle_type_adjustment_per_vehicle_analysis_report import \
    ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysisReport
from .inbound_and_outbound_vehicle_capacity_analysis_report import InboundAndOutboundVehicleCapacityAnalysisReport
from .inbound_to_outbound_vehicle_capacity_utilization_analysis_report import \
    InboundToOutboundVehicleCapacityUtilizationAnalysisReport
from .modal_split_analysis_report import ModalSplitAnalysisReport
from .quay_side_throughput_analysis_report import QuaySideThroughputAnalysisReport
from .truck_gate_throughput_analysis_report import TruckGateThroughputAnalysisReport
from .yard_capacity_analysis_report import YardCapacityAnalysisReport
from ..reporting import AbstractReport
from ..reporting.auto_reporter import AutoReporter
from ..reporting.output_style import DisplayAsMarkupLanguage

logger = logging.getLogger("conflowgen")

reports: typing.Iterable[typing.Type[AbstractReport]] = [
    InboundAndOutboundVehicleCapacityAnalysisReport,
    ContainerFlowByVehicleTypeAnalysisReport,
    ContainerFlowAdjustmentByVehicleTypeAnalysisReport,
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport,
    ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysisReport,
    ModalSplitAnalysisReport,
    ContainerDwellTimeAnalysisReport,
    QuaySideThroughputAnalysisReport,
    TruckGateThroughputAnalysisReport,
    YardCapacityAnalysisReport,
    InboundToOutboundVehicleCapacityUtilizationAnalysisReport
]


def run_all_analyses(
        as_text: bool = True,
        as_graph: bool = False,
        display_text_func: typing.Optional[typing.Callable] = None,
        display_in_markup_language: typing.Union[DisplayAsMarkupLanguage, str, None] = None,
        static_graphs: bool = False,
        display_as_ipython_svg: bool = False,
        start_date: typing.Optional[datetime.datetime] = None,
        end_date: typing.Optional[datetime.datetime] = None
) -> None:
    """
    Runs all post-hoc analyses in sequence.
    This is just a convenience function to ensure that all reports are presented.
    The text output is logged to the logger with the name 'conflowgen' by default..
    See
    :func:`setup_logger`
    for more details.

    If neither ``static_graphs`` nor ``display_as_ipython_svg`` are true, the default functionality of the respective
    plotting library is used.

    Args:
        as_text: Whether to get the reports as text and log them
        as_graph: Whether to display the reports as graphs (visualizations will pop up)
        display_text_func: The function to use to display the text. Defaults to :meth:`logger.info`.
        display_in_markup_language: The markup language to use. Currently, the options 'markdown' and 'plaintext' exist.
            Defaults to :class:`.DisplayAsPlainText` (same as 'plaintext'), users can provide their own approach with
            :class:`.DisplayAsMarkupLanguage`.
        static_graphs: Whether the graphs should be static. Plotly has some nice interactive options that are currently
            not supported inside some websites such as the HTML version of the documentation. In such cases, the static
            version of the plots is used.
        display_as_ipython_svg: Whether the graphs should be plotted with the IPython functionality. This is suitable,
            e.g., inside Jupyter Notebooks where a conversion to a raster image is not desirable.
        start_date:
            Only include containers that arrive after the given start time (if supported by the report).
        end_date:
            Only include containers that depart before the given end time (if supported by the report).
    """
    auto_reporter = AutoReporter(
        as_text=as_text,
        as_graph=as_graph,
        display_text_func=display_text_func,
        display_in_markup_language=display_in_markup_language,
        static_graphs=static_graphs,
        display_as_ipython_svg=display_as_ipython_svg,
        start_date=start_date,
        end_date=end_date
    )

    auto_reporter.output.display_explanation(
        "Run all analyses on the synthetically generated data."
    )
    auto_reporter.present_reports(reports)
    auto_reporter.output.display_explanation("All analyses have been run.")
