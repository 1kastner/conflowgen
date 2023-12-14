import datetime
import logging
import typing

from conflowgen.reporting import AbstractReport
from conflowgen.reporting.output_style import DisplayAsMarkupLanguage, DisplayAsPlainText, DisplayAsMarkdown


class AutoReporter:

    logger = logging.getLogger("conflowgen")

    def __init__(
            self,
            as_text: bool,
            as_graph: bool,
            display_text_func: typing.Optional[typing.Callable],
            display_in_markup_language: typing.Union[DisplayAsMarkupLanguage, str, None],
            static_graphs: bool,
            display_as_ipython_svg: bool,
            start_date: typing.Optional[datetime.datetime],
            end_date: typing.Optional[datetime.datetime]
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
        self.display_as_ipython_svg = display_as_ipython_svg

        self.start_date = start_date
        self.end_date = end_date

    @staticmethod
    def _get_report_name(report_instance: object) -> str:
        class_name: str = report_instance.__class__.__name__
        class_name_with_spaces = ''.join(map(lambda x: x if x.islower() else " " + x, class_name))
        return class_name_with_spaces.strip()

    def present_reports(self, reports: typing.Iterable[typing.Type[AbstractReport]]):
        for report in reports:
            report_instance = report()
            name_of_report = self._get_report_name(report_instance)
            self.output.display_headline(name_of_report)
            self.output.display_explanation(report_instance.report_description)
            if self.as_text:
                if self.start_date is not None or self.end_date is not None:
                    report_as_text = report_instance.get_report_as_text(
                        start_date=self.start_date,
                        end_date=self.end_date
                    )
                else:
                    report_as_text = report_instance.get_report_as_text()
                assert report_as_text, "Report should not be empty"
                self.output.display_verbatim(report_as_text)
            if self.as_graph:
                try:
                    if self.start_date is not None or self.end_date is not None:
                        report_instance.show_report_as_graph(
                            static=self.static_graphs,
                            display_as_ipython_svg=self.display_as_ipython_svg,
                            start_date=self.start_date,
                            end_date=self.end_date
                        )
                    else:
                        report_instance.show_report_as_graph(
                            static=self.static_graphs,
                            display_as_ipython_svg=self.display_as_ipython_svg,
                         )
                except NotImplementedError:
                    self.output.display_explanation(
                        f"Skipping {report} as no graph version of the report is implemented"
                    )
