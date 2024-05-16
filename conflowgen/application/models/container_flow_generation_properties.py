import datetime

from peewee import AutoField, CharField, DateField, TimestampField, DateTimeField, FloatField

from conflowgen.domain_models.seeders import DEFAULT_TRANSPORTATION_BUFFER
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

    ramp_up_period= FloatField(
        default=0,
        help_text="Number of days for the ramp-up period"
    )

    ramp_down_period = FloatField(
        default=0,
        help_text="Number of days for the ramp-down period"
    )

    generated_at = DateTimeField(
        default=lambda: datetime.datetime.now().replace(microsecond=0),
        help_text="The date the these properties have been created"
    )

    last_updated_at = TimestampField(
        help_text="The date these properties has been last updated"
    )

    transportation_buffer = FloatField(
        default=DEFAULT_TRANSPORTATION_BUFFER,
    )
