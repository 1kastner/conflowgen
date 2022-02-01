import logging
from typing import Iterable, Type, Callable, Optional, Union

from .abstract_preview_report import AbstractPreviewReport
from .inbound_and_outbound_vehicle_capacity_preview_report import InboundAndOutboundVehicleCapacityPreviewReport
from .container_flow_by_vehicle_type_preview_report import ContainerFlowByVehicleTypePreviewReport
from .modal_split_preview_report import ModalSplitPreviewReport
from .vehicle_capacity_exceeded_preview_report import VehicleCapacityExceededPreviewReport
from ..reporting.output_style import DisplayInMarkupLanguage, DisplayAsPlainText, DisplayAsMarkdown

logger = logging.getLogger("conflowgen")


report_order: Iterable[Type[AbstractPreviewReport]] = [
    InboundAndOutboundVehicleCapacityPreviewReport,
    VehicleCapacityExceededPreviewReport,
    ContainerFlowByVehicleTypePreviewReport,
    ModalSplitPreviewReport,
]


def run_all_previews(
        as_text: bool = True,
        as_graph: bool = False,
        display_text_func: Optional[Callable] = logger.info,
        display_in_markup_language: Union[DisplayInMarkupLanguage, str, None] = None
) -> None:
    """
    Runs all preview analyses in sequence.
    This is just a convenience function to ensure that all reports are presented.
    The text output is logged to the logger with the name 'conflowgen'.
    See
    :func:`setup_logger`
    for more details.

    Args:
        as_text: Whether to get the reports as text and log them.
        as_graph: Whether to display the reports as graphs (visualizations will pop up).
        display_text_func: The function to use to display the text. Defaults to :meth:`logger.info`.
        display_in_markup_language: The output style for certain markup languages.
            Defaults to :class:`.PlainOutputStyle`
    """
    assert as_text or as_graph, "At least one of the two modes should be chosen"

    output = {
        None: DisplayAsPlainText(display_text_func),
        "plaintext": DisplayAsPlainText(display_text_func),
        "markdown": DisplayAsMarkdown(display_text_func)
    }.get(display_in_markup_language, display_in_markup_language)

    output.display_explanation("Run all previews for the input distributions in combination with the schedules.")

    for report in report_order:
        report_instance = report()
        output.display_headline(report_instance.__class__.__name__)
        output.display_explanation(report_instance.report_description)
        if as_text:
            report_as_text = report_instance.get_report_as_text()
            output.display_verbatim(report_as_text)
        if as_graph:
            try:
                report_instance.show_report_as_graph()
            except NotImplementedError:
                output.display_explanation(f"Skipping {report} as no graph version of the report is implemented")

    output.display_explanation("All previews have been presented.")
