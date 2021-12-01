import datetime

from peewee import AutoField, CharField, DateField, TimestampField, DateTimeField, IntegerField, FloatField

from conflowgen.domain_models.base_model import BaseModel


class ContainerFlowGenerationProperties(BaseModel):
    """
    This table should only have a single entry.
    """
    id = AutoField()
    name = CharField(
        null=True,
        help_text="The name of the generated container Flow, e.g. a scenario"
    )
    start_date = DateField(
        null=True,
        help_text="The first day of the generated container Flow"
    )
    end_date = DateField(
        null=True,
        help_text="The last day of the generated container Flow"
    )
    generated_at = DateTimeField(
        default=datetime.datetime.now,
        help_text="The date the these properties have been created"
    )
    last_updated_at = TimestampField(
        help_text="The date these properties has been last updated"
    )
    maximum_dwell_time_of_import_containers_in_hours = IntegerField(
        default=(3 * 24),
        help_text="The maximum dwell time for import containers is set by the container terminal operators. "
                  "In practice, a later pickup would typically result in additional storage charges and is thus "
                  "avoided by supply chain partners. The default value of 3 days is inspired by the pricing policy of "
                  "HHLA as described in "
                  "https://hhla.de/fileadmin/download/HHLA_Kaitarif_2021_09_01_en.pdf"
    )
    minimum_dwell_time_of_import_containers_in_hours = IntegerField(
        default=3,
        help_text="The minimum dwell time is the earliest time after the discharging and loading process has started "
                  "that a truck tries to pick up the container. In practice, this is often determined by the IT system "
                  "of the terminal operators which releases a container for being picked up once the container is on "
                  "the terminal (it has been successfully been discharged). The actual earliest feasible point is "
                  "determined in the simulation model because here no sequence of discharge is determined, i.e. the "
                  "container might be still on the vessel when the truck arrives. Thus, this value must be checked for "
                  "when using the synthetic data in e.g. a simulation model or mathematical model."
    )
    maximum_dwell_time_of_export_containers_in_hours = IntegerField(
        default=(5 * 24),
        help_text="The maximum dwell time for export containers is set by the container terminal. In practice, "
                  "typically trucks are simply not allowed to deliver the container earlier than this. "
                  "See e.g.: https://hhla.de/fileadmin/download/HHLA_Kaitarif_2021_09_01_en.pdf"
    )
    minimum_dwell_time_of_export_containers_in_hours = IntegerField(
        default=12,
        help_text="The minimum dwell time is the minimum time a container must reside on the terminal before the "
                  "vessel discharging and loading process starts. This time is needed for e.g. finalizing the stowage "
                  "planning and avoiding that a container which is designated for a vessel arrives shortly before "
                  "vessel departure. If the vehicle that delivers this container is waiting in a queue, actually the "
                  "container might miss the vessel. This cut-off is typically defined by the shipping company. "
                  "Here, as a simplification one cut-off period is used for all cases."
    )
    maximum_dwell_time_of_transshipment_containers_in_hours = IntegerField(
        default=(7 * 24),
        help_text="The maximum dwell time for transshipment is the maximum time difference of arrival between two "
                  "vessels. The value of 7 days is inspired by "
                  "https://hhla.de/fileadmin/download/HHLA_Kaitarif_2021_09_01_en.pdf."
    )
    minimum_dwell_time_of_transshipment_containers_in_hours = IntegerField(
        default=3,
        help_text="The minimum dwell time for transshipment is the minimum time difference of arrival between two "
                  "vessels. This means that one vessel can request a container from another vessel if and only if "
                  "the previous vessel has arrived these k hours before the first one. For short transshipment dwell "
                  "times, it might result in a direct transfer from one vessel to the other without any storage. "
                  "Larger values will result in more conservative handling times. Container groups are not considered, "
                  "the generated container flow data might not be digestible by a simulation model without additional "
                  "adjustments of the input data."
    )
    transportation_buffer = FloatField(
        default=.2,
        help_text="The export buffer describes how much more a vehicle typically takes from the terminal compared to "
                  "the amount of containers in TEU which it delivers. The value '.2' means that 20% more than the "
                  "moved capacity (which determines the containers that are delivered to the terminal) is available "
                  "for exporting containers as long as the maximum capacity of the vehicle is not exceeded. This "
                  "concept has been proposed in "
                  'Hartmann, Sönke. "Generating scenarios for simulation and optimization of container terminal '
                  'logistics." Or Spectrum 26.2 (2004): 171-192.'
    )
