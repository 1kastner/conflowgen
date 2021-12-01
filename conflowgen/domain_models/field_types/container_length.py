from __future__ import annotations

from peewee import IntegerField

from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.field_types.enum_database_field import cast_to_db_value


class ContainerLengthField(IntegerField):
    """
    This class enable a Enum like field for peewee
    """

    def db_value(self, value):
        return cast_to_db_value(value)

    def python_value(self, value):
        return ContainerLength(value)
