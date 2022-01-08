"""
The intention of this script is to provide a demonstration of how ConFlowGen is supposed to be used as a library.
It is, by design, a stateful library that persists all input in an SQL database format to enable reproducibility.
The intention of this demo is further explained in the logs it generated.
"""

import datetime
import os.path
import random
import sys
import pandas as pd

try:
    import conflowgen
    print(f"Importing ConFlowGen version {conflowgen.__version__}")
except ImportError:
    print("Please first install conflowgen as a library")
    sys.exit()

# The seed of x=1 guarantees that the same traffic data is generated as input data in this script. However, it does not
# affect the container generation or the assignment of containers to vehicles.
seeded_random = random.Random(x=1)

import_deham_dir = os.path.join(
    os.path.dirname(sys.modules[__name__].__file__),
    "data",
    "DEHAM",
    "CT Altenwerder"
)
df_deep_sea_vessels = pd.read_csv(
    os.path.join(
        import_deham_dir,
        "deep_sea_vessel_input.csv"
    ),
    index_col=[0]
)
df_feeders = pd.read_csv(
    os.path.join(
        import_deham_dir,
        "feeder_input.csv"
    ),
    index_col=[0]
)
df_barges = pd.read_csv(
    os.path.join(
        import_deham_dir,
        "barge_input.csv"
    ),
    index_col=[0]
)
df_trains = pd.read_csv(
    os.path.join(
        import_deham_dir,
        "train_input.csv"
    ),
    index_col=[0]
)

# Start logging
logger = conflowgen.setup_logger()

logger.info("""
####
## Demo DEHAM CTA
####
This is a demo based on some publicly available figures, some educated guesses, and some random assumptions due to the
lack of information regarding the Container Terminal Altenwerder (CTA) in the port of Hamburg. While this demo only
poorly reflects processes in place, in addition this is only a (poor) snapshot of what has been happening in summer
2021.

No affiliations with the container terminal operators exist. Then why this example was chosen? This is an extension of
the work of Sönke Hartmann [1] and he presented some sample figures. For showing the similarities and differences,
similar assumptions have been made throughout this demo.

[1] Hartmann, S.: Generating scenarios for simulation and optimization of container terminal logistics. OR Spectrum,
vol. 26, 171–192 (2004). doi: 10.1007/s00291-003-0150-6
""")
# Pick database
database_chooser = conflowgen.DatabaseChooser()
demo_file_name = "demo_deham_cta.sqlite"
if demo_file_name in database_chooser.list_all_sqlite_databases():
    database_chooser.load_existing_sqlite_database(demo_file_name)
else:
    database_chooser.create_new_sqlite_database(demo_file_name, assume_tas=True)

# Set settings
container_flow_generation_manager = conflowgen.ContainerFlowGenerationManager()
# Data is available for 01.07.2021 to 31.07.2021 - you can also pick a shorter time period. However, there are some
# artifacts in the generated data in the beginning and in the end of the time range because containers can not continue
# their journey as intended, i.e. they must be delivered by or picked up by a truck since no vehicles that move
# according to a schedule are generated before the start and after the end.
container_flow_start_date = datetime.date(year=2021, month=7, day=1)
container_flow_end_date = datetime.date(year=2021, month=7, day=31)
container_flow_generation_manager.set_properties(
    name="Demo DEHAM CTA",
    start_date=container_flow_start_date,
    end_date=container_flow_end_date
)

# Set some general assumptions regarding the container properties
container_length_distribution_manager = conflowgen.ContainerLengthDistributionManager()
container_length_distribution_manager.set_container_lengths({
    conflowgen.ContainerLength.twenty_feet: 0.33,
    conflowgen.ContainerLength.forty_feet: 0.67,
    conflowgen.ContainerLength.forty_five_feet: 0,
    conflowgen.ContainerLength.other: 0
})

# Add vehicles that frequently visit the terminal.
port_call_manager = conflowgen.PortCallManager()

logger.info("Start importing feeder vessels...")
for i, row in df_feeders.iterrows():
    feeder_vehicle_name = row["vehicle_name"] + "-unique"
    capacity = row["capacity"]
    vessel_arrives_at_as_pandas_type = row["arrival (planned)"]
    vessel_arrives_at_as_datetime_type = pd.to_datetime(vessel_arrives_at_as_pandas_type)

    if vessel_arrives_at_as_datetime_type.date() < container_flow_start_date:
        logger.info(f"Skipping feeder '{feeder_vehicle_name}' because it arrives before the start")
        continue

    if vessel_arrives_at_as_datetime_type.date() > container_flow_end_date:
        logger.info(f"Skipping feeder '{feeder_vehicle_name}' because it arrives after the end")
        continue

    if port_call_manager.has_schedule(feeder_vehicle_name, vehicle_type=conflowgen.ModeOfTransport.feeder):
        logger.info(f"Skipping feeder '{feeder_vehicle_name}' because it already exists")
        continue

    logger.info(f"Add feeder '{feeder_vehicle_name}' to database")
    # The estimate is based on the reported lifts per call in "Tendency toward Mega Containerships and the Constraints
    # of Container Terminals" of Park and Suh (2019) J. Mar. Sci. Eng, URL: https://www.mdpi.com/2077-1312/7/5/131/htm
    # lifts per call refer to both the inbound and outbound journey of the vessel
    moved_capacity = int(round(capacity * seeded_random.triangular(0.3, 0.8) / 2))  # this is only the inbound journey

    # The actual name of the port is not important as it is only used to group containers that are destined for the same
    # vessel in the yard for faster loading (less reshuffling). The assumption that the same amount of containers is
    # destined for each of the following ports is a simplification.
    number_ports = int(round(seeded_random.triangular(low=2, high=4)))
    next_ports = [
        (port_name, 1/number_ports)
        for port_name in [
            f"port {i + 1} of {feeder_vehicle_name}"
            for i in range(number_ports)
        ]
    ]

    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.feeder,
        service_name=feeder_vehicle_name,
        vehicle_arrives_at=vessel_arrives_at_as_datetime_type.date(),
        vehicle_arrives_at_time=vessel_arrives_at_as_datetime_type.time(),
        average_vehicle_capacity=capacity,
        average_moved_capacity=moved_capacity,
        vehicle_arrives_every_k_days=-1,  # single arrival, no frequent schedule
        next_destinations=next_ports
    )
logger.info("Feeder vessels are imported")

logger.info("Start importing deep sea vessels...")
for i, row in df_deep_sea_vessels.iterrows():
    deep_sea_vessel_vehicle_name = row["vehicle_name"] + "-unique"
    capacity = row["capacity"]
    vessel_arrives_at_as_pandas_type = row["arrival (planned)"]
    vessel_arrives_at_as_datetime_type = pd.to_datetime(vessel_arrives_at_as_pandas_type)

    if vessel_arrives_at_as_datetime_type.date() < container_flow_start_date:
        logger.info(f"Skipping deep sea vessel '{deep_sea_vessel_vehicle_name}' because it arrives before the start")
        continue

    if vessel_arrives_at_as_datetime_type.date() > container_flow_end_date:
        logger.info(f"Skipping deep sea vessel '{deep_sea_vessel_vehicle_name}' because it arrives after the end")
        continue

    if port_call_manager.has_schedule(deep_sea_vessel_vehicle_name,
                                      vehicle_type=conflowgen.ModeOfTransport.deep_sea_vessel):
        logger.info(f"Skipping deep sea service '{deep_sea_vessel_vehicle_name}' because it already exists")
        continue

    logger.info(f"Add deep sea vessel '{deep_sea_vessel_vehicle_name}' to database")
    # The estimate is based on the reported lifts per call in "Tendency toward Mega Containerships and the Constraints
    # of Container Terminals" of Park and Suh (2019) J. Mar. Sci. Eng, URL: https://www.mdpi.com/2077-1312/7/5/131/htm
    # lifts per call refer to both the inbound and outbound journey of the vessel
    moved_capacity = int(round(capacity * seeded_random.triangular(0.3, 0.6) / 2))  # this is only the inbound journey

    # The actual name of the port is not important as it is only used to group containers that are destined for the same
    # vessel in the yard for faster loading (less reshuffling). The assumption that the same amount of containers is
    # destined for each of the following ports is a simplification
    number_ports = int(round(seeded_random.triangular(low=3, high=15, mode=7)))
    next_ports = [
        (port_name, 1/number_ports)
        for port_name in [
            f"port {i + 1} of {deep_sea_vessel_vehicle_name}"
            for i in range(number_ports)
        ]
    ]

    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.deep_sea_vessel,
        service_name=deep_sea_vessel_vehicle_name,
        vehicle_arrives_at=vessel_arrives_at_as_datetime_type.date(),
        vehicle_arrives_at_time=vessel_arrives_at_as_datetime_type.time(),
        average_vehicle_capacity=capacity,
        average_moved_capacity=moved_capacity,
        vehicle_arrives_every_k_days=-1,  # single arrival, no frequent schedule
        next_destinations=next_ports
    )
logger.info("Deep sea vessels are imported")

logger.info("Start importing barges...")
for i, row in df_barges.iterrows():
    barge_vehicle_name = row["vehicle_name"] + "-unique"
    capacity = row["capacity"]
    vessel_arrives_at_as_pandas_type = row["arrival (planned)"]
    vessel_arrives_at_as_datetime_type = pd.to_datetime(vessel_arrives_at_as_pandas_type)

    if vessel_arrives_at_as_datetime_type.date() < container_flow_start_date:
        logger.info(f"Skipping barge '{barge_vehicle_name}' because it arrives before the start")
        continue

    if vessel_arrives_at_as_datetime_type.date() > container_flow_end_date:
        logger.info(f"Skipping barge '{barge_vehicle_name}' because it arrives after the end")
        continue

    if port_call_manager.has_schedule(barge_vehicle_name, vehicle_type=conflowgen.ModeOfTransport.barge):
        logger.info(f"Skipping barge '{barge_vehicle_name}' because it already exists")
        continue

    logger.info(f"Add barge '{barge_vehicle_name}' to database")
    # assume that the barge approaches 2 or more terminals, thus not the whole barge is available for CTA
    moved_capacity = int(round(capacity * seeded_random.uniform(0.3, 0.6)))
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.barge,
        service_name=barge_vehicle_name,
        vehicle_arrives_at=vessel_arrives_at_as_datetime_type.date(),
        vehicle_arrives_at_time=vessel_arrives_at_as_datetime_type.time(),
        average_vehicle_capacity=capacity,
        average_moved_capacity=moved_capacity,
        vehicle_arrives_every_k_days=-1  # single arrival, no frequent schedule
    )
logger.info("Barges are imported")

logger.info("Start importing trains...")
for i, row in df_trains.iterrows():
    train_vehicle_name = row["vehicle_name"]
    vessel_arrives_at_as_pandas_type = row["arrival_day"]
    vessel_arrives_at_as_datetime_type = pd.to_datetime(vessel_arrives_at_as_pandas_type)

    if port_call_manager.has_schedule(train_vehicle_name, vehicle_type=conflowgen.ModeOfTransport.train):
        logger.info(f"Train service '{train_vehicle_name}' already exists")
        continue

    capacity = 96  # in TEU, see https://www.intermodal-info.com/verkehrstraeger/
    earliest_time = datetime.time(hour=1, minute=0)
    earliest_time_as_delta = datetime.timedelta(hours=earliest_time.hour, minutes=earliest_time.minute)
    latest_time = datetime.time(hour=5, minute=30)
    latest_time_as_delta = datetime.timedelta(hours=latest_time.hour, minutes=latest_time.minute)
    number_slots_minus_one = int((latest_time_as_delta - earliest_time_as_delta) / datetime.timedelta(minutes=30))

    drawn_slot = seeded_random.randint(0, number_slots_minus_one)
    vehicle_arrives_at_time_as_delta = earliest_time_as_delta + datetime.timedelta(hours=0.5 * drawn_slot)
    vehicle_arrives_at_time = (datetime.datetime.min + vehicle_arrives_at_time_as_delta).time()
    logger.info(f"Add train '{train_vehicle_name}' to database")
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.train,
        service_name=train_vehicle_name,
        vehicle_arrives_at=vessel_arrives_at_as_datetime_type.date(),
        vehicle_arrives_at_time=vehicle_arrives_at_time,
        average_vehicle_capacity=capacity,
        average_moved_capacity=capacity,  # discharge everything
        vehicle_arrives_every_k_days=7  # weekly arrival
    )

logger.info("All trains are imported")

logger.info("All vehicles have been imported")

###
# Now, all schedules and input distributions are set up - no further inputs are required
###

logger.info("Preview the results with some light-weight approaches.")

conflowgen.run_all_previews()

logger.info("Generate all fleets with all vehicles. This is the core of the whole project.")
container_flow_generation_manager.generate()

logger.info("The container flow data have been generated, run post-hoc analyses on them")

conflowgen.run_all_posthoc_analyses()

logger.info("For a better understanding of the data, it is advised to study the logs and compare the preview with the "
            "post-hoc analysis results")

logger.info("Start data export...")

# Export important entries from SQL to CSV so that it can be further processed, e.g. by a simulation software
export_container_flow_manager = conflowgen.ExportContainerFlowManager()
export_container_flow_manager.export(
    folder_name="demo-DEHAM-of-day--" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "--").split(".")[0],
    file_format=conflowgen.ExportFileFormat.csv
)

# Gracefully close everything
database_chooser.close_current_connection()
logger.info("Demo 'demo_DEHAM_CTA' finished successfully.")
