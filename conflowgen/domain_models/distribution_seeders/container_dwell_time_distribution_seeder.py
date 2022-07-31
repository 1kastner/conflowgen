from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository


DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS = 3
"""
The minimum dwell time of import containers is the earliest time after the discharging and loading process has started
that a vehicle arrives from the hinterland and tries to pick up the container.
In practice, this is often determined by the IT system of the terminal operators which releases a container for being
picked up once the container is on the terminal (it has been successfully discharged).
The actual earliest feasible point is determined in the subsequent model which consumes the generated data because here
no sequence of discharge is determined, i.e., the container might be still on the vessel when the truck arrives.
Thus, this value must be checked for when using the synthetic data in, e.g., a simulation model or mathematical model.
"""

DEFAULT_MINIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS = 12
"""
The minimum dwell time of export containers is the minimum time a container must reside on the terminal before the
vessel discharging and loading process starts.
This time is needed for, e.g., finalizing the stowage planning and avoiding that a container which is designated for a
vessel arrives shortly before vessel departure.
If the vehicle that delivers this container is waiting in a queue, actually the container might miss the vessel.
This cut-off is typically defined by the shipping company.
Here, as a simplification one cut-off period is used for all cases.
Both the time interval and the logic are inspired by expert interviews.
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


#: This container dwell time distribution is based on
#: :cite:p:`cto2021interview`.
#: The average container dwell times are taken from a report but of course only reflect the reality at a given time for
#: a specific container terminal operator.
#: The variance of the distribution just serves as an approximation.
DEFAULT_AVERAGE_CONTAINER_DWELL_TIMES = {

    ModeOfTransport.truck: {
        ModeOfTransport.truck: {
            StorageRequirement.empty: 18.8,
            **{
                container_type: 7.1
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.train: {
            StorageRequirement.empty: 11.5,
            **{
                container_type: 1.7
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.barge: {
            StorageRequirement.empty: 7.4,
            **{
                container_type: 10
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.feeder: {
            StorageRequirement.empty: 13.0,
            **{
                container_type: 3.58
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.deep_sea_vessel: {
            StorageRequirement.empty: 13.4,
            **{
                container_type: 6.5
                for container_type in StorageRequirement.get_full_containers()
            }
        },
    },

    ModeOfTransport.train: {
        ModeOfTransport.truck: {
            StorageRequirement.empty: 9.5,
            **{
                container_type: 2.9
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.train: {
            StorageRequirement.empty: 8.3,
            **{
                container_type: 12
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.barge: {
            StorageRequirement.empty: 8.1,
            **{
                container_type: 14.6
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.feeder: {
            StorageRequirement.empty: 16,
            **{
                container_type: 4.1
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.deep_sea_vessel: {
            StorageRequirement.empty: 12.8,
            **{
                container_type: 6.7
                for container_type in StorageRequirement.get_full_containers()
            }
        },
    },

    ModeOfTransport.barge: {
        ModeOfTransport.truck: {
            StorageRequirement.empty: 9.6,
            **{
                container_type: 8
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.train: {
            StorageRequirement.empty: 8.2,
            **{
                container_type: 10
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.barge: {
            StorageRequirement.empty: 11.6,
            **{
                container_type: 4.5
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.feeder: {
            StorageRequirement.empty: 14.4,
            **{
                container_type: 4.2
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.deep_sea_vessel: {
            StorageRequirement.empty: 17.6,
            **{
                container_type: 6.8
                for container_type in StorageRequirement.get_full_containers()
            }
        },
    },

    ModeOfTransport.feeder: {
        ModeOfTransport.truck: {
            StorageRequirement.empty: 13.6,
            **{
                container_type: 3.1
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.train: {
            StorageRequirement.empty: 13.6,
            **{
                container_type: 4
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.barge: {
            StorageRequirement.empty: 8.2,
            **{
                container_type: 2.4
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.feeder: {
            StorageRequirement.empty: 10.6,
            **{
                container_type: 3.8
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.deep_sea_vessel: {
            StorageRequirement.empty: 14.6,
            **{
                container_type: 8.3
                for container_type in StorageRequirement.get_full_containers()
            }
        },
    },

    ModeOfTransport.deep_sea_vessel: {
        ModeOfTransport.truck: {
            StorageRequirement.empty: 12.2,
            **{
                container_type: 3
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.train: {
            StorageRequirement.empty: 11,
            **{
                container_type: 3
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.barge: {
            StorageRequirement.empty: 11.2,
            **{
                container_type: 2.5
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.feeder: {
            StorageRequirement.empty: 14,
            **{
                container_type: 4.3
                for container_type in StorageRequirement.get_full_containers()
            }
        },
        ModeOfTransport.deep_sea_vessel: {
            StorageRequirement.empty: 27.7,
            **{
                container_type: 9.3
                for container_type in StorageRequirement.get_full_containers()
            }
        },
    }
}


_export = {
    ModeOfTransport.truck: 0,
    ModeOfTransport.train: 0,
    ModeOfTransport.barge: 0,
    ModeOfTransport.feeder: DEFAULT_MINIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS,
    ModeOfTransport.deep_sea_vessel: DEFAULT_MINIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS
}

_import_or_transshipment = {
    ModeOfTransport.truck: DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS,
    ModeOfTransport.train: DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS,
    ModeOfTransport.barge: DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS,
    ModeOfTransport.feeder: DEFAULT_MINIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS,
    ModeOfTransport.deep_sea_vessel: DEFAULT_MINIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS
}

#: The minimum container dwell times are an absolute value in hours.
#: Three different cases are considered:
#: - .. autodata:: DEFAULT_MINIMUM_DWELL_TIME_OF_IMPORT_CONTAINERS_IN_HOURS
#: - .. autodata:: DEFAULT_MINIMUM_DWELL_TIME_OF_EXPORT_CONTAINERS_IN_HOURS
#: - .. autodata:: DEFAULT_MINIMUM_DWELL_TIME_OF_TRANSSHIPMENT_CONTAINERS_IN_HOURS
#: These are composed into the origin-destination matrix.
DEFAULT_MINIMUM_DWELL_TIMES_IN_HOURS = {
    ModeOfTransport.truck: _export,
    ModeOfTransport.train: _export,
    ModeOfTransport.barge: _export,
    ModeOfTransport.feeder: _import_or_transshipment,
    ModeOfTransport.deep_sea_vessel: _import_or_transshipment
}


DEFAULT_CONTAINER_DWELL_TIME_DISTRIBUTIONS = {
    from_vehicle: {
        to_vehicle: {
            requirement: {
                "distribution_name":
                    "lognormal",
                "average_number_of_hours":
                    DEFAULT_AVERAGE_CONTAINER_DWELL_TIMES[from_vehicle][to_vehicle][requirement] * 24,
                "variance":
                    DEFAULT_AVERAGE_CONTAINER_DWELL_TIMES[from_vehicle][to_vehicle][requirement] * 24 * 25,
                "maximum_number_of_hours":
                    DEFAULT_AVERAGE_CONTAINER_DWELL_TIMES[from_vehicle][to_vehicle][requirement] * 24 * 3,
                "minimum_number_of_hours":
                    DEFAULT_MINIMUM_DWELL_TIMES_IN_HOURS[from_vehicle][to_vehicle]
            } for requirement in StorageRequirement
        } for to_vehicle in ModeOfTransport
    } for from_vehicle in ModeOfTransport
}


def seed():
    repository = ContainerDwellTimeDistributionRepository()
    repository.set_distributions(DEFAULT_CONTAINER_DWELL_TIME_DISTRIBUTIONS)
