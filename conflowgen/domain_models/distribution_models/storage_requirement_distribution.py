from peewee import FloatField, CompositeKey

from conflowgen.domain_models.base_model import BaseModel
from conflowgen.domain_models.field_types.container_length import ContainerLengthField
from conflowgen.domain_models.field_types.storage_requirement import StorageRequirementField


class StorageRequirementDistribution(BaseModel):
    """The storage requirement distribution of the containers depending on the container length"""
    container_length = ContainerLengthField(null=False)
    storage_requirement = StorageRequirementField(null=False)
    fraction = FloatField(null=False)

    def __repr__(self):
        return f"<StorageRequirementDistribution storage_requirement: {self.storage_requirement}; " \
               f"fraction: {self.fraction}>"

    class Meta:
        primary_key = CompositeKey('container_length', 'storage_requirement')
