import abc
from typing import Callable
from textwrap import dedent, fill


def _remove_unnecessary_spaces(text):
    return dedent(text).strip()


class DisplayAsMarkupLanguage(abc.ABC):
    """
    This is the abstract class new markup language definitions can derive from.
    """
    
    @abc.abstractmethod
    def display_headline(self, text: str, level: int) -> None:
        """
        Args:
            text: The text of the headline
            level: The level of the headline, 1 being the upmost headline. The number of levels depends on the markup
                language
        """
        ...

    @abc.abstractmethod
    def display_verbatim(self, text: str) -> None:
        """
        Args:
            text: The text of the verbatim block (show as-is)
        """
        ...

    @abc.abstractmethod
    def display_explanation(self, text: str) -> None:
        """
        Args:
            text: The text of an explanatory text (show in normal font, wrap as required).
                Different paragraphs are separated by repeated invocations of this method.
        """
        ...


class DisplayAsPlainText(DisplayAsMarkupLanguage):
    """
    With this style, the output is simply returned in a plain manner.
    This is e.g. helpful when logging the text.
    """

    DESIRED_LINE_LENGTH = 80  # doc: The console width used for wrapping output to new lines. This is not mandatory.

    def __init__(self, display_text_func: Callable):
        self.display_text_func = display_text_func

    def display_headline(self, text: str, level: int = -1):
        """
        Args:
            text: The text of the headline.
            level: The level of the headline is not supported for the plaintext mode.
        """
        self.display_text_func("\n" + text + "\n")

    def display_verbatim(self, text: str):
        self.display_text_func(text)

    def display_explanation(self, text: str):
        text = fill(_remove_unnecessary_spaces(text), width=self.DESIRED_LINE_LENGTH)
        self.display_text_func(text)


class DisplayAsMarkdown(DisplayAsMarkupLanguage):
    """
    With this style, the output is set in Markdown.
    This is e.g. helpful when showing the output in Jupyter Notebooks.
    """
    def __init__(self, display_markdown_func: Callable):
        self.display_markdown_func = display_markdown_func

    def display_headline(self, text: str, level: int = 3):
        self.display_markdown_func("#" * level + " " + text + "\n")

    def display_verbatim(self, text: str):
        self.display_markdown_func("\n```\n" + text + "\n```\n")

    def display_explanation(self, text: str):
        self.display_markdown_func(_remove_unnecessary_spaces(text))
