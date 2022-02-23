
DEFAULT_MAXIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS = (3 * 24)
"""
The maximum dwell time for import containers is set by the container terminal operators.
In practice, a later pickup would typically result in additional storage charges and is thus avoided by supply chain
partners.
The default value of 3 days is inspired by the pricing policy of HHLA as described in
:cite:p:`hhla.quay.tariff.2021`
"""

DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS = 3
"""
The minimum dwell time is the earliest time after the discharging and loading process has started that a truck tries to
pick up the container.
In practice, this is often determined by the IT system  of the terminal operators which releases a container for being
picked up once the container is on the terminal (it has been successfully been discharged).
The actual earliest feasible point is determined in the subsequent model which consumes the generated data because here
no sequence of discharge is determined, i.e. the container might be still on the vessel when the truck arrives.
Thus, this value must be checked for when using the synthetic data in e.g. a simulation model or mathematical model.
"""

DEFAULT_MAXIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS = (5 * 24)
"""
The maximum dwell time for export containers is set by the container terminal.
In practice, typically trucks are simply not allowed to deliver the container earlier than this.
The default value of 5 days is inspired by the pricing policy of HHLA as described in
:cite:p:`hhla.quay.tariff.2021`
"""

DEFAULT_MINIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS = 12
"""
The minimum dwell time is the minimum time a container must reside on the terminal before the vessel discharging and
loading process starts.
This time is needed for e.g. finalizing the stowage planning and avoiding that a container which is designated for a
vessel arrives shortly before vessel departure.
If the vehicle that delivers this container is waiting in a queue, actually the container might miss the vessel.
This cut-off is typically defined by the shipping company.
Here, as a simplification one cut-off period is used for all cases.
Both the time intervall and the logic are inspired by expert interviews.
"""

DEFAULT_MAXIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS = (7 * 24)
"""
The maximum dwell time for transshipment is the maximum time difference of arrival between two vessels.
The value of 7 days is inspired by
:cite:p:`hhla.quay.tariff.2021`
"""

DEFAULT_MINIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS = 3
"""
The minimum dwell time for transshipment is the minimum time difference of arrival between two vessels.
This means that one vessel can request a container from another vessel if and only if the previous vessel has arrived
these k hours before the first one.
For short transshipment dwell times, it might result in a direct transfer from one vessel to the other without any
storage if the user decides to support such activities in their model (such as a simulation model or optimization
model).
"""

DEFAULT_TRANSPORTATION_BUFFER = 0.2
"""
The export buffer describes how much more a vehicle typically takes from the terminal compared to the amount of
containers in TEU which it delivers.
The value ``.2`` means that 20% more than the moved capacity (which determines the containers that are delivered to the
terminal) is available for exporting containers as long as the maximum capacity of the vehicle is not exceeded.
This concept has been first proposed by
:cite:t:`hartmann2004generating`.
"""
