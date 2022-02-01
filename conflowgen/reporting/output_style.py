import abc
from typing import Callable
from textwrap import dedent, fill


def remove_unnecessary_spaces(text):
    return dedent(text).strip()


class DisplayInMarkupLanguage(abc.ABC):
    """
    Every logging message
    """
    @abc.abstractmethod
    def display_headline(self, text: str):
        ...

    @abc.abstractmethod
    def display_verbatim(self, text: str):
        ...

    @abc.abstractmethod
    def display_explanation(self, text: str):
        ...


class DisplayAsPlainText(DisplayInMarkupLanguage):
    """
    With this style, the output is simply returned in a plain manner.
    """

    DESIRED_LINE_LENGTH = 80  # doc: The console width used for wrapping output to new lines. This is not mandatory.

    def __init__(self, display_text_func: Callable):
        self.display_text_func = display_text_func

    def display_headline(self, text: str):
        self.display_text_func("\n" + text + "\n")

    def display_verbatim(self, text: str):
        self.display_text_func(text)

    def display_explanation(self, text: str):
        text = fill(remove_unnecessary_spaces(text), width=self.DESIRED_LINE_LENGTH)
        self.display_text_func(text)


class DisplayAsMarkdown(DisplayInMarkupLanguage):
    """
    With this style, the output is set in Markdown
    """
    def __init__(self, display_markdown_func: Callable):
        self.display_markdown_func = display_markdown_func

    def display_headline(self, text: str, level: int = 3):
        self.display_markdown_func("#" * level + " " + text + "\n")

    def display_verbatim(self, text: str):
        self.display_markdown_func("\n```\n" + text + "\n```\n")

    def display_explanation(self, text: str):
        self.display_markdown_func(remove_unnecessary_spaces(text))
