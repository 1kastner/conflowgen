from peewee import FloatField, CompositeKey

from conflowgen.domain_models.base_model import BaseModel
from conflowgen.domain_models.field_types.mode_of_transport import ModeOfTransportField


class ModeOfTransportDistribution(BaseModel):
    """The origin-destination distribution in terms of mode of transport for the containers"""
    delivered_by = ModeOfTransportField(null=False)
    picked_up_by = ModeOfTransportField(null=False)
    fraction = FloatField(null=False)

    class Meta:
        primary_key = CompositeKey('delivered_by', 'picked_up_by')
