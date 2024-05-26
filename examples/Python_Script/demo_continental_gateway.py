"""
This is an example of a continental gateway that only receives feeder vessels and uses trucks to connect to the
hinterland. The vessel arrivals are based on the DEHAM CTA example.
"""

import datetime
import os.path
import random
import sys
import pandas as pd

try:
    import conflowgen
    install_dir = os.path.abspath(
        os.path.join(conflowgen.__file__, os.path.pardir)
    )
    print(f"Importing ConFlowGen version {conflowgen.__version__} installed at {install_dir}.")
except ImportError as exc:
    print("Please first install ConFlowGen, e.g. with conda or pip")
    raise exc

# The seed of x=1 guarantees that the same traffic data is generated as input data in this script. However, it does not
# affect the container generation or the assignment of containers to vehicles.
seeded_random = random.Random(x=1)

with_visuals = False
if len(sys.argv) > 2:
    if sys.argv[2] == "--with-visuals":
        with_visuals = True

this_dir = os.path.dirname(__file__)

import_deham_dir = os.path.join(
    this_dir,
    "data",
    "DEHAM",
    "CT Altenwerder"
)
df_feeders = pd.read_csv(
    os.path.join(
        import_deham_dir,
        "feeder_input.csv"
    ),
    index_col=[0]
)


# Start logging
logger = conflowgen.setup_logger()
logger.info(__doc__)

# Pick database
database_chooser = conflowgen.DatabaseChooser(
    sqlite_databases_directory=os.path.join(this_dir, "databases")
)
demo_file_name = "demo_continental_gateway.sqlite"
database_chooser.create_new_sqlite_database(
    demo_file_name,
    assume_tas=True,
    overwrite=True
)

# Set settings
container_flow_generation_manager = conflowgen.ContainerFlowGenerationManager()
container_flow_start_date = datetime.date(year=2021, month=7, day=1)
container_flow_end_date = datetime.date(year=2021, month=7, day=31)
container_flow_generation_manager.set_properties(
    name="Demo Continental Gateway",
    start_date=container_flow_start_date,
    end_date=container_flow_end_date
)

# Set some general assumptions regarding the container properties
container_length_distribution_manager = conflowgen.ContainerLengthDistributionManager()
container_length_distribution_manager.set_container_length_distribution({
    conflowgen.ContainerLength.twenty_feet: 0.33,
    conflowgen.ContainerLength.forty_feet: 0.67,
    conflowgen.ContainerLength.forty_five_feet: 0,
    conflowgen.ContainerLength.other: 0
})

mode_of_transport_distribution_manager = conflowgen.ModeOfTransportDistributionManager()
mode_of_transport_distribution_manager.set_mode_of_transport_distribution(
    {
        conflowgen.ModeOfTransport.feeder: {
            conflowgen.ModeOfTransport.train: 0,
            conflowgen.ModeOfTransport.truck: 1,
            conflowgen.ModeOfTransport.barge: 0,
            conflowgen.ModeOfTransport.feeder: 0,
            conflowgen.ModeOfTransport.deep_sea_vessel: 0
        },
        conflowgen.ModeOfTransport.truck: {
            conflowgen.ModeOfTransport.train: 0,
            conflowgen.ModeOfTransport.truck: 0,
            conflowgen.ModeOfTransport.barge: 0,
            conflowgen.ModeOfTransport.feeder: 1,
            conflowgen.ModeOfTransport.deep_sea_vessel: 0
        },

        # The following entries cannot be missing but won't be actually used. They do not matter because no vehicles of
        # that kind are generated as we do not add any schedules for them.
        conflowgen.ModeOfTransport.barge: {
            conflowgen.ModeOfTransport.train: 0.2,
            conflowgen.ModeOfTransport.truck: 0.15,
            conflowgen.ModeOfTransport.barge: 0.25,
            conflowgen.ModeOfTransport.feeder: 0.1,
            conflowgen.ModeOfTransport.deep_sea_vessel: 0.3
        },
        conflowgen.ModeOfTransport.deep_sea_vessel: {
            conflowgen.ModeOfTransport.train: 0.25,
            conflowgen.ModeOfTransport.truck: 0.1,
            conflowgen.ModeOfTransport.barge: 0.2,
            conflowgen.ModeOfTransport.feeder: 0.15,
            conflowgen.ModeOfTransport.deep_sea_vessel: 0.3
        },
        conflowgen.ModeOfTransport.train: {
            conflowgen.ModeOfTransport.train: 0.3,
            conflowgen.ModeOfTransport.truck: 0.1,
            conflowgen.ModeOfTransport.barge: 0.15,
            conflowgen.ModeOfTransport.feeder: 0.2,
            conflowgen.ModeOfTransport.deep_sea_vessel: 0.25
        }
    }
)

# Add vehicles that frequently visit the terminal.
port_call_manager = conflowgen.PortCallManager()

logger.info("Start importing feeder vessels...")
for i, row in df_feeders.iterrows():
    feeder_vehicle_name = row["vehicle_name"]
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

    port_call_manager.add_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.feeder,
        service_name=feeder_vehicle_name,
        vehicle_arrives_at=vessel_arrives_at_as_datetime_type.date(),
        vehicle_arrives_at_time=vessel_arrives_at_as_datetime_type.time(),
        vehicle_capacity=capacity,
        inbound_container_volume=moved_capacity,
        next_destinations=next_ports
    )
logger.info("Feeder vessels are imported")

###
# Now, all schedules and input distributions are set up - no further inputs are required
###

logger.info("Preview the results with some light-weight approaches.")

conflowgen.run_all_previews(as_graph=True)

logger.info("Generate all fleets with all vehicles. This is the core of the whole project.")
container_flow_generation_manager.generate()

logger.info("The container flow data have been generated, run analyses on them.")

conflowgen.run_all_analyses(as_graph=True)

logger.info("For a better understanding of the data, it is advised to study the logs and compare the preview with the "
            "analysis results.")

# Gracefully close everything
database_chooser.close_current_connection()

logger.info(f"ConFlowGen {conflowgen.__version__} from {conflowgen.__file__} was used.")
logger.info("Demo 'demo_continental_gateway' finished successfully.")
