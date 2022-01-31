from __future__ import annotations
import enum

import enum_tools.documentation


@enum_tools.documentation.document_enum
class ContainerLength(enum.Enum):
    """
    The container length is one of the most important factors of how much space a container occupies. Here, the most
    common container sizes (neglecting height) are represented.
    """

    twenty_feet = 20  # doc: A twenty-foot container

    forty_feet = 40  # doc: A forty-foot container

    forty_five_feet = 45  # doc: A forty-five-foot container

    other = -1  # doc: Any other length usually does not fit into the standardized slots and handling processes.

    @classmethod
    def get_factor(cls, container_length: ContainerLength) -> float:
        """
        Args:
            container_length: The length of the sea container

        Returns: The TEU factor of that container
        """
        return {
            cls.twenty_feet: 1,
            cls.forty_feet: 2,
            cls.forty_five_feet: 2.25,
            cls.other: 2.5  # This is assumed to be a bad shape taking a lot of capacity.
        }[container_length]

    def __str__(self) -> str:
        """
        The textual representation is e.g. '20 feet' instead of '<ContainerLength.twenty_feet>' so it is easier to read
        in the logs.
        """
        if self.value > 0:
            return f"{self.value} feet"
        return "other"

    @classmethod
    def cast_element_type(cls, text: str) -> ContainerLength | None:
        """
        Args:
            text: The text to parse

        Returns:
            The container length enum entry if the cast was successful, ``None`` otherwise.
        """
        if text == "other":
            return cls.other
        feet_suffix = " feet"
        if text.endswith(feet_suffix):
            number_part = text[:-len(feet_suffix)]
            if not number_part.isdigit():
                return None
            casted_number_part = int(number_part)
            return cls(casted_number_part)
        return None
