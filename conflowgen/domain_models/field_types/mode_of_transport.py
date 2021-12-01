from __future__ import annotations

from peewee import TextField

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.field_types.enum_database_field import cast_to_db_value


class ModeOfTransportField(TextField):
    """
    This class enable a Enum like field for Peewee
    """

    def db_value(self, value):
        return cast_to_db_value(value)

    def python_value(self, value):
        return ModeOfTransport(value)
