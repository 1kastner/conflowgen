from peewee import TextField

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.field_types.enum_database_field import cast_to_db_value


class StorageRequirementField(TextField):
    """
    This class enable a Enum like field for peewee
    """

    def db_value(self, value):
        return cast_to_db_value(value)

    def python_value(self, value):
        return StorageRequirement(value)
