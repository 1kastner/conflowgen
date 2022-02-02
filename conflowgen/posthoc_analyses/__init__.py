import logging
from typing import Iterable, Type, Optional, Union, Callable

from .abstract_posthoc_analysis_report import AbstractPosthocAnalysisReport
from .inbound_and_outbound_vehicle_capacity_analysis_report import InboundAndOutboundVehicleCapacityAnalysisReport
from .container_flow_by_vehicle_type_analysis_report import ContainerFlowByVehicleTypeAnalysisReport
from .modal_split_analysis_report import ModalSplitAnalysisReport
from .container_flow_adjustment_by_vehicle_type_analysis_report import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisReport
from .container_flow_adjustment_by_vehicle_type_analysis_summary_report import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport
from .quay_side_throughput_analysis_report import QuaySideThroughputAnalysisReport
from .truck_gate_throughput_analysis_report import TruckGateThroughputAnalysisReport
from .yard_capacity_analysis_report import YardCapacityAnalysisReport
from ..reporting.output_style import DisplayAsMarkupLanguage, DisplayAsPlainText, DisplayAsMarkdown

logger = logging.getLogger("conflowgen")


report_order: Iterable[Type[AbstractPosthocAnalysisReport]] = [
    InboundAndOutboundVehicleCapacityAnalysisReport,
    ContainerFlowByVehicleTypeAnalysisReport,
    ContainerFlowAdjustmentByVehicleTypeAnalysisReport,
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport,
    ModalSplitAnalysisReport,
    QuaySideThroughputAnalysisReport,
    TruckGateThroughputAnalysisReport,
    YardCapacityAnalysisReport
]


def run_all_analyses(
        as_text: bool = True,
        as_graph: bool = False,
        display_text_func: Optional[Callable] = None,
        display_in_markup_language: Union[DisplayAsMarkupLanguage, str, None] = None
) -> None:
    """
    Runs all post-hoc analyses in sequence.
    This is just a convenience function to ensure that all reports are presented.
    The text output is logged to the logger with the name 'conflowgen'.
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
    """
    assert as_text or as_graph, "At least one of the two modes should be chosen"

    if display_text_func is None:
        display_text_func = logger.info

    output = {
        None: DisplayAsPlainText(display_text_func),
        "plaintext": DisplayAsPlainText(display_text_func),
        "markdown": DisplayAsMarkdown(display_text_func)
    }.get(display_in_markup_language, display_in_markup_language)

    output.display_explanation("Run all post-hoc analyses on the synthetically generated data")

    for report in report_order:
        report_instance = report()
        output.display_headline(report_instance.__class__.__name__)
        output.display_explanation(report_instance.report_description)
        if as_text:
            report_as_text = report_instance.get_report_as_text()
            output.display_explanation(report_as_text)
        if as_graph:
            try:
                report_instance.show_report_as_graph()
            except NotImplementedError:
                output.display_explanation(f"Skipping {report} as no graph version of the report is implemented")

    output.display_explanation("All post-hoc analyses have been run.")
