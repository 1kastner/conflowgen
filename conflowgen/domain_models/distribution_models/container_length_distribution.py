from peewee import FloatField

from conflowgen.domain_models.base_model import BaseModel
from conflowgen.domain_models.field_types.container_length import ContainerLengthField


class ContainerLengthDistribution(BaseModel):
    """The length distribution of the containers"""
    container_length = ContainerLengthField(null=False, primary_key=True, unique=True)
    fraction = FloatField(null=False)

    def __repr__(self):
        return f"<ContainerLengthDistribution length: {self.container_length}; " \
               f"fraction: {self.fraction}>"
