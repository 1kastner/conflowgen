from peewee import FloatField, IntegerField, CompositeKey

from conflowgen.domain_models.base_model import BaseModel
from conflowgen.domain_models.field_types.container_length import ContainerLengthField


class ContainerWeightDistribution(BaseModel):
    """The weight distribution of the containers"""
    container_length = ContainerLengthField(null=False)
    weight_category = IntegerField(null=False)
    fraction = FloatField(null=False)

    def __repr__(self):
        return f"<ContainerWeightDistributionEntry length: {self.container_length}; " \
               f"weight: {self.weight_category}; fraction: {self.fraction}>"

    class Meta:
        primary_key = CompositeKey('container_length', 'weight_category')
