import datetime

from peewee import AutoField, CharField, DateField, TimestampField, DateTimeField, IntegerField, FloatField

from conflowgen.domain_models.seeders import DEFAULT_MAXIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS, \
    DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS, \
    DEFAULT_MAXIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS, \
    DEFAULT_MINIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS, \
    DEFAULT_MAXIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS, \
    DEFAULT_MINIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS, DEFAULT_TRANSPORTATION_BUFFER
from conflowgen.domain_models.base_model import BaseModel


class ContainerFlowGenerationProperties(BaseModel):
    """
    This table should only have a single entry.
    """
    id = AutoField()

    name = CharField(
        null=True,
        help_text="The name of the generated container flow, e.g. a scenario"
    )

    start_date = DateField(
        null=True,
        help_text="The first day of the generated container flow"
    )

    end_date = DateField(
        null=True,
        help_text="The last day of the generated container flow"
    )

    generated_at = DateTimeField(
        default=datetime.datetime.now,
        help_text="The date the these properties have been created"
    )

    last_updated_at = TimestampField(
        help_text="The date these properties has been last updated"
    )

    maximum_dwell_time_of_import_containers_in_hours = IntegerField(
        default=DEFAULT_MAXIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS
    )

    minimum_dwell_time_of_import_containers_in_hours = IntegerField(
        default=DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS
    )
    maximum_dwell_time_of_export_containers_in_hours = IntegerField(
        default=DEFAULT_MAXIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS,
    )
    minimum_dwell_time_of_export_containers_in_hours = IntegerField(
        default=DEFAULT_MINIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS,
    )
    maximum_dwell_time_of_transshipment_containers_in_hours = IntegerField(
        default=DEFAULT_MAXIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS,
    )
    minimum_dwell_time_of_transshipment_containers_in_hours = IntegerField(
        default=DEFAULT_MINIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS,
    )
    transportation_buffer = FloatField(
        default=DEFAULT_TRANSPORTATION_BUFFER,
    )
