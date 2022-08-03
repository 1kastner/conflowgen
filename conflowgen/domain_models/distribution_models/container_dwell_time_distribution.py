from peewee import FloatField, CompositeKey, TextField

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.base_model import BaseModel
from conflowgen.domain_models.field_types.mode_of_transport import ModeOfTransportField
from conflowgen.domain_models.field_types.storage_requirement import StorageRequirementField


class ContainerDwellTimeDistributionInterface:

    #: The vehicle type the box is delivered by.
    delivered_by: ModeOfTransport

    #: The vehicle type the box is picked up by.
    picked_up_by: ModeOfTransport

    #: The storage requirement of the box.
    storage_requirement: StorageRequirement

    #: The distribution to use in that specific case.
    distribution_name: str

    #: To avoid unrealistic short times, values shorter than this are not drawn from the distribution.
    minimum_number_of_hours: float

    #: To avoid unrealistic long times, values longer than this are not drawn from the distribution.
    maximum_number_of_hours: float

    #: The average number of hours is the expected mean of the distribution.
    average_number_of_hours: float

    #: The variance is a distribution-specific parameter and helps to instantiate, e.g., normal or lognormal
    #: distributions.
    variance: float


class ContainerDwellTimeDistribution(BaseModel, ContainerDwellTimeDistributionInterface):
    """
    The container dwell time distribution describes how long the container remains in the yard.
    """
    delivered_by = ModeOfTransportField(null=False)
    picked_up_by = ModeOfTransportField(null=False)
    storage_requirement = StorageRequirementField(null=False)

    distribution_name = TextField(null=False)
    minimum_number_of_hours = FloatField(default=0)
    maximum_number_of_hours = FloatField(default=-1)
    average_number_of_hours = FloatField(null=False)

    variance = FloatField(null=True)

    class Meta:
        primary_key = CompositeKey('delivered_by', 'picked_up_by', 'storage_requirement')
