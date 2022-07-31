
DEFAULT_TRANSPORTATION_BUFFER = 0.2
"""
The export buffer describes how much more a vehicle typically takes from the terminal compared to the amount of
containers in TEU which it delivers.
The value ``.2`` means that 20% more than the moved capacity (which determines the containers that are delivered to the
terminal) is available for exporting containers as long as the maximum capacity of the vehicle is not exceeded.
This concept has been first proposed by
:cite:t:`hartmann2004generating`.
"""
