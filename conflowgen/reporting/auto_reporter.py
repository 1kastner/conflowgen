import logging
from typing import Optional, Callable, Union, Iterable, Type

from conflowgen.reporting import AbstractReport
from conflowgen.reporting.output_style import DisplayAsMarkupLanguage, DisplayAsPlainText, DisplayAsMarkdown


class AutoReporter:

    logger = logging.getLogger("conflowgen")

    def __init__(
            self,
            as_text: bool,
            as_graph: bool,
            display_text_func: Optional[Callable],
            display_in_markup_language: Union[DisplayAsMarkupLanguage, str, None],
            static_graphs: bool
    ):
        assert as_text or as_graph, "At least one of the two modes should be chosen"

        self.as_text = as_text
        self.as_graph = as_graph

        if display_text_func is None:
            display_text_func = self.logger.info

        self.output = {
            None: DisplayAsPlainText(display_text_func),
            "plaintext": DisplayAsPlainText(display_text_func),
            "markdown": DisplayAsMarkdown(display_text_func)
        }.get(display_in_markup_language, display_in_markup_language)

        self.static_graphs = static_graphs

    def present_reports(self, reports: Iterable[Type[AbstractReport]]):
        for report in reports:
            report_instance = report()
            name_of_report = report_instance.__class__.__name__
            self.output.display_headline(name_of_report)
            self.output.display_explanation(report_instance.report_description)
            if self.as_text:
                report_as_text = report_instance.get_report_as_text()
                self.output.display_verbatim(report_as_text)
            if self.as_graph:
                try:
                    report_instance.show_report_as_graph(static=self.static_graphs)
                except NotImplementedError:
                    self.output.display_explanation(
                        f"Skipping {report} as no graph version of the report is implemented"
                    )
