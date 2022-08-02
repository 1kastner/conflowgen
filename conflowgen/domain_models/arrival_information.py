from peewee import AutoField, DateTimeField

from conflowgen.domain_models.base_model import BaseModel


class TruckArrivalInformationForPickup(BaseModel):
    """
    This is the information that is available on a vehicle based on the status of the container.
    """
    id = AutoField()
    planned_container_pickup_time_prior_berthing = DateTimeField(
        null=True,
        help_text="At the time of berthing, do we know when the container will be picked up? "
                  "null means that is not the case, otherwise the time is provided. "
                  "This information could be used for allocating a good container slot."
    )
    planned_container_pickup_time_after_initial_storage = DateTimeField(
        null=True,
        help_text="Some time after the container is stored in the yard, "
                  "do we know when the container will be picked up? "
                  "null means that is not the case, otherwise the time is provided. "
                  "This information could be used for housekeeping."
    )
    realized_container_pickup_time = DateTimeField(
        null=False,
        help_text="At this time, the container is finally picked up.")


class TruckArrivalInformationForDelivery(BaseModel):
    """
    This is the information that is available on a vehicle based on the status of the container.
    """
    id = AutoField()
    planned_container_delivery_time_at_window_start = DateTimeField(
        null=True,
        help_text="Terminals often allow trucks only to deliver a container a fixed timerange before "
                  "its scheduled departure from the terminal by deep sea vessel or feeder. "
                  "This information could be used for yard template planning, i.e. reserving container slots."
    )
    realized_container_delivery_time = DateTimeField(
        null=False,
        help_text="At this time, the container is finally delivered."
    )
