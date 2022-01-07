import logging
from typing import Iterable, Type
from textwrap import dedent, fill

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


def run_all_posthoc_analyses(as_text: bool = True, as_graph: bool = False) -> None:
    """
    Runs all post-hoc analyses so that the user does not need to invoke all instances.
    The text output is logged to the logger with the name 'conflowgen'.
    See
    :func:`setup_logger`
    for more details.

    Args:
        as_text: Whether to get the reports as text and log them
        as_graph: Whether to display the reports as graphs

    Returns:

    """
    assert as_text or as_graph, "At least one of the two modes should be chosen"

    logger.info("Run all post-hoc analyses on the synthetically generated data")

    for report in report_order:
        report_instance = report()
        logger.info(f"Analysis report: {report_instance.__class__.__name__}")
        # noinspection PyTypeChecker
        report_description: str = report_instance.report_description
        introduction_of_report = fill(dedent(report_description).strip(), width=80)
        logger.info(introduction_of_report)
        if as_text:
            report_as_text = report_instance.get_report_as_text()
            logger.info(report_as_text)
        if as_graph:
            try:
                report_instance.show_report_as_graph()
            except NotImplementedError:
                logger.info(f"Skipping {report} as no graph version of the report is implemented")

    logger.info("All post-hoc analyses have been run.")
