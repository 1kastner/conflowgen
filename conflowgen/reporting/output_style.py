import abc
from typing import Callable
from textwrap import dedent, fill


def _remove_unnecessary_spaces(text):
    return dedent(text).strip()


class DisplayAsMarkupLanguage(abc.ABC):
    """
    This is the abstract class new markup language definitions can derive from.
    """
    def __init__(self, display_func: Callable):
        """
        Args:
            display_func: The function that is invoked to display the text
        """
        self.display_func = display_func

    @abc.abstractmethod
    def display_headline(self, text: str, level: int) -> None:
        """
        Args:
            text: The text of the headline
            level: The level of the headline, 1 being the upmost headline. The number of levels depends on the markup
                language.
        """
        ...

    @abc.abstractmethod
    def display_verbatim(self, text: str) -> None:
        """
        Args:
            text: The text of the verbatim block (shown as-is)
        """
        ...

    @abc.abstractmethod
    def display_explanation(self, text: str) -> None:
        """
        Args:
            text: The text of an explanatory text (shown in normal font, wrapped if required).
                  Different paragraphs are separated by repeated invocations of this method.
        """
        ...


class DisplayAsPlainText(DisplayAsMarkupLanguage):
    """
    With this style, the output is simply returned in a plain manner.
    This is e.g. helpful when logging the text.
    """

    DESIRED_LINE_LENGTH = 80  # doc: The console width used for wrapping output to new lines. This is not mandatory.

    def display_headline(self, text: str, level: int = -1) -> None:
        """
        Args:
            text: The text of the headline.
            level: The level of the headline is not supported for the plaintext mode.
        """
        self.display_func("\n" + text + "\n")

    def display_verbatim(self, text: str) -> None:
        self.display_func(text)

    def display_explanation(self, text: str) -> None:
        text = fill(_remove_unnecessary_spaces(text), width=self.DESIRED_LINE_LENGTH)
        self.display_func(text)


class DisplayAsMarkdown(DisplayAsMarkupLanguage):
    """
    With this style, the output is set in Markdown.
    This is, e.g., helpful when showing the output in Jupyter Notebooks.
    """

    def display_headline(self, text: str, level: int = 4) -> None:
        self.display_func("#" * level + " " + text + "\n")

    def display_verbatim(self, text: str) -> None:
        self.display_func("\n```\n" + text + "\n```\n")

    def display_explanation(self, text: str) -> None:
        self.display_func(_remove_unnecessary_spaces(text))
