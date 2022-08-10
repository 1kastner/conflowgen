from typing import Iterable, Type, Callable, Optional, Union

from .inbound_and_outbound_vehicle_capacity_preview_report import InboundAndOutboundVehicleCapacityPreviewReport
from .container_flow_by_vehicle_type_preview_report import ContainerFlowByVehicleTypePreviewReport
from .modal_split_preview_report import ModalSplitPreviewReport
from .vehicle_capacity_exceeded_preview_report import VehicleCapacityUtilizationOnOutboundJourneyPreviewReport
from ..reporting import AbstractReport
from ..reporting.auto_reporter import AutoReporter
from ..reporting.output_style import DisplayAsMarkupLanguage


reports: Iterable[Type[AbstractReport]] = [
    InboundAndOutboundVehicleCapacityPreviewReport,
    VehicleCapacityUtilizationOnOutboundJourneyPreviewReport,
    ContainerFlowByVehicleTypePreviewReport,
    ModalSplitPreviewReport,
]


def run_all_previews(
        as_text: bool = True,
        as_graph: bool = False,
        display_text_func: Optional[Callable] = None,
        display_in_markup_language: Union[DisplayAsMarkupLanguage, str, None] = None,
        static_graphs: bool = False
) -> None:
    """
    Runs all preview analyses in sequence.
    This is just a convenience function to ensure that all reports are presented.
    The text output is logged to the logger with the name 'conflowgen' by default.
    See
    :func:`setup_logger`
    for more details.

    Args:
        as_text: Whether to get the reports as text and log them.
        as_graph: Whether to display the reports as graphs (visualizations will pop up).
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
        "Run all previews for the input distributions in combination with the schedules."
    )
    auto_reporter.present_reports(reports)
    auto_reporter.output.display_explanation("All previews have been presented.")
