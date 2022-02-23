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
        Each container occupies a certain amount of space when stored.
         This required space is measured in TEU.

        .. note::
            .. autodata:: conflowgen.domain_models.data_types.container_length.CONTAINER_LENGTH_TO_OCCUPIED_TEU

        Args:
            container_length: The length of the container

        Returns:
            The TEU factor of the container
        """
        return CONTAINER_LENGTH_TO_OCCUPIED_TEU[container_length]

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
            The container length enum name if the cast was successful, ``None`` otherwise.
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


CONTAINER_LENGTH_TO_OCCUPIED_TEU = {
    ContainerLength.twenty_feet: 1,
    ContainerLength.forty_feet: 2,
    ContainerLength.forty_five_feet: 2.25,
    ContainerLength.other: 2.5
}
"""
This is the translation table to specify the occupied storage space in TEU.
For 20', 40', and 45', the typical values are picked.
The TEU factor for the value 'other' is chosen to be rather large because it is assumed to be difficult to find a proper
storage position.
"""
