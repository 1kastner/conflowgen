import logging
from typing import Optional, Union, Callable, Iterable, Type

from .container_flow_adjustment_by_vehicle_type_analysis_report import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisReport
from .container_flow_adjustment_by_vehicle_type_analysis_summary_report import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport
from .container_flow_by_vehicle_type_analysis_report import ContainerFlowByVehicleTypeAnalysisReport
from .container_flow_by_vehicle_type_analysis_report import ContainerFlowByVehicleTypeAnalysisReport
from .inbound_and_outbound_vehicle_capacity_analysis_report import InboundAndOutboundVehicleCapacityAnalysisReport
from .inbound_and_outbound_vehicle_capacity_analysis_report import InboundAndOutboundVehicleCapacityAnalysisReport
from .inbound_to_outbound_vehicle_capacity_utilization_analysis_report import \
    InboundToOutboundVehicleCapacityUtilizationAnalysisReport
from .modal_split_analysis_report import ModalSplitAnalysisReport
from .modal_split_analysis_report import ModalSplitAnalysisReport
from .quay_side_throughput_analysis_report import QuaySideThroughputAnalysisReport
from .truck_gate_throughput_analysis_report import TruckGateThroughputAnalysisReport
from .yard_capacity_analysis_report import YardCapacityAnalysisReport
from ..reporting import AbstractReport
from ..reporting.auto_reporter import AutoReporter
from ..reporting.output_style import DisplayAsMarkupLanguage

logger = logging.getLogger("conflowgen")

reports: Iterable[Type[AbstractReport]] = [
    InboundAndOutboundVehicleCapacityAnalysisReport,
    ContainerFlowByVehicleTypeAnalysisReport,
    ContainerFlowAdjustmentByVehicleTypeAnalysisReport,
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport,
    ModalSplitAnalysisReport,
    QuaySideThroughputAnalysisReport,
    TruckGateThroughputAnalysisReport,
    YardCapacityAnalysisReport,
    InboundToOutboundVehicleCapacityUtilizationAnalysisReport
]


def run_all_analyses(
        as_text: bool = True,
        as_graph: bool = False,
        display_text_func: Optional[Callable] = None,
        display_in_markup_language: Union[DisplayAsMarkupLanguage, str, None] = None,
        static_graphs: bool = False
) -> None:
    """
    Runs all post-hoc analyses in sequence.
    This is just a convenience function to ensure that all reports are presented.
    The text output is logged to the logger with the name 'conflowgen' by default..
    See
    :func:`setup_logger`
    for more details.

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
    """
    auto_reporter = AutoReporter(
        as_text=as_text,
        as_graph=as_graph,
        display_text_func=display_text_func,
        display_in_markup_language=display_in_markup_language,
        static_graphs=static_graphs
    )

    auto_reporter.output.display_explanation(
        "Run all analyses on the synthetically generated data."
    )
    auto_reporter.present_reports(reports)
    auto_reporter.output.display_explanation("All post-hoc analyses have been run.")
