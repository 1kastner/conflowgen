from __future__ import annotations
import enum
import enum_tools.documentation


@enum_tools.documentation.document_enum
class StorageRequirement(enum.Enum):
    """
    A container is stored in different areas of the yard depending on its requirements.
    """

    # pylint: disable=line-too-long

    empty = "empty"  # doc: An empty container is typically stored in an empty container yard

    standard = "standard"
    """A standard container is typically stored in the full container yard and makes up most of the containers passing 
    through a terminal"""

    reefer = "reefer"
    """A reefer container requires electricity (i.e., a reefer plug) to keep the inner temperature on a low level
    """

    dangerous_goods = "dangerous_goods"
    """A dangerous goods container needs a specially prepared storage area so they do not constitute a major hazard to 
    health and environment."""

    def __str__(self):
        """
        The representation is e.g. 'reefer' instead of '<StorageRequirement.reefer>' and thus nicer for the logs.
        """
        return self.value
