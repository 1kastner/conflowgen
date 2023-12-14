from peewee import AutoField, CharField, IntegerField, BooleanField

from conflowgen.domain_models.base_model import BaseModel


class RandomSeedStore(BaseModel):
    """
    This table contains a random seed for each class or function that contains randomness
    """
    id = AutoField()

    name = CharField(
        help_text="The name of the class, function, or other type of object."
    )

    is_random = BooleanField(
        help_text="Whether the value is meant to change between invocations of the generation process."
    )

    random_seed = IntegerField(
        help_text="The last used random seed."
    )
