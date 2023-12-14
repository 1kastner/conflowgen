from peewee import FloatField

from conflowgen.domain_models.base_model import BaseModel


class TruckArrivalDistribution(BaseModel):
    """The truck arrival distribution (both inbound and outbound journeys)"""
    hour_in_the_week = FloatField(null=False, primary_key=True, unique=True)
    fraction = FloatField(null=False)

    def __repr__(self):
        return f"<TruckArrivalDistribution hour in the week: {self.hour_in_the_week}; " \
               f"fraction: {self.fraction}>"
