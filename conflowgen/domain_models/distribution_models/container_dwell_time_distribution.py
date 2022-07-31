from peewee import FloatField, CompositeKey, TextField

from conflowgen.domain_models.base_model import BaseModel
from conflowgen.domain_models.field_types.mode_of_transport import ModeOfTransportField
from conflowgen.domain_models.field_types.storage_requirement import StorageRequirementField


class ContainerDwellTimeDistribution(BaseModel):
    """The distribution of how long the container remains in the yard."""

    # The key: The distribution depends on which vehicle delivers the container, which picks it up, and the type
    delivered_by = ModeOfTransportField(null=False)
    picked_up_by = ModeOfTransportField(null=False)
    storage_requirement = StorageRequirementField(null=False)

    # Clipping: Allows to avoid extreme and unreasonable values
    minimum_number_of_hours = FloatField(default=0)
    maximum_number_of_hours = FloatField(default=-1)

    # Describing the actual distribution
    distribution_name = TextField(null=False)
    average_number_of_hours = FloatField(null=False)
    variance = FloatField(null=True)

    class Meta:
        primary_key = CompositeKey('delivered_by', 'picked_up_by', 'storage_requirement')
