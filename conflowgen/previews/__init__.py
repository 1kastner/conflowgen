import logging
from textwrap import dedent, fill
from typing import Iterable, Type

from .abstract_preview_report import AbstractPreviewReport
from .inbound_and_outbound_vehicle_capacity_preview_report import InboundAndOutboundVehicleCapacityPreviewReport
from .container_flow_by_vehicle_type_preview_report import ContainerFlowByVehicleTypePreviewReport
from .modal_split_preview_report import ModalSplitPreviewReport
from .vehicle_capacity_exceeded_preview_report import VehicleCapacityExceededPreviewReport
from ..logging.logging import DESIRED_LINE_LENGTH

logger = logging.getLogger("conflowgen")


report_order: Iterable[Type[AbstractPreviewReport]] = [
    InboundAndOutboundVehicleCapacityPreviewReport,
    VehicleCapacityExceededPreviewReport,
    ContainerFlowByVehicleTypePreviewReport,
    ModalSplitPreviewReport,
]


def run_all_previews(as_text: bool = True, as_graph: bool = False) -> None:
    """
    Runs all preview analyses in sequence.
    This is just a convenience function to ensure that all reports are presented.
    The text output is logged to the logger with the name 'conflowgen'.
    See
    :func:`setup_logger`
    for more details.

    Args:
        as_text: Whether to get the reports as text and log them
        as_graph: Whether to display the reports as graphs (visualizations will pop up)
    """
    assert as_text or as_graph, "At least one of the two modes should be chosen"

    logger.info("Run all previews for the input distributions in combination with the schedules.")

    for report in report_order:
        report_instance = report()
        logger.info(f"Preview: {report_instance.__class__.__name__}")
        # noinspection PyTypeChecker
        report_description: str = report_instance.report_description
        introduction_of_report = fill(dedent(report_description).strip(), width=DESIRED_LINE_LENGTH)
        logger.info(introduction_of_report)
        if as_text:
            report_as_text = report_instance.get_report_as_text()
            logger.info(report_as_text)
        if as_graph:
            try:
                report_instance.show_report_as_graph()
            except NotImplementedError:
                logger.info(f"Skipping {report} as no graph version of the report is implemented")

    logger.info("All previews have been presented.")
