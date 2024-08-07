"""
Demo Proof of Concept (PoC)
===========================

This demo is based on some example data and is meant to show the basic functionality. For a slightly more realistic
example, please check out `demo_DEHAM_CTA.py`. However, computing those numbers also takes longer than quickly running
this small example.

The intention of this script is to provide a demonstration of how ConFlowGen is supposed to be used as a library.
It is, by design, a stateful library that persists all input in an SQL database format to enable reproducibility.
The intention of this demo is further explained in the logs it generated.
"""

import datetime
import os.path
import sys
import subprocess

try:
    import conflowgen
    install_dir = os.path.abspath(
        os.path.join(conflowgen.__file__, os.path.pardir)
    )
    print(f"Importing ConFlowGen version {conflowgen.__version__} installed at {install_dir}.")
except ImportError as exc:
    print("Please first install ConFlowGen, e.g. with conda or pip")
    raise exc


this_dir = os.path.dirname(__file__)

with_visuals = False
if len(sys.argv) > 2:
    if sys.argv[2] == "--with-visuals":
        with_visuals = True

# Start logging
logger = conflowgen.setup_logger()
logger.info(__doc__)

# Pick database
database_chooser = conflowgen.DatabaseChooser(
    sqlite_databases_directory=os.path.join(this_dir, "databases")
)
demo_file_name = "demo_poc.sqlite"
database_chooser.create_new_sqlite_database(
    demo_file_name,
    assume_tas=True,
    overwrite=True
)


# Set settings
container_flow_generation_manager = conflowgen.ContainerFlowGenerationManager()
container_flow_generation_manager.set_properties(
    name="Demo file",
    start_date=datetime.datetime.now().date(),
    end_date=datetime.datetime.now().date() + datetime.timedelta(days=21)
)

port_call_manager = conflowgen.PortCallManager()

# Add vehicles that frequently visit the terminal.
feeder_service_name = "LX050"
logger.info(f"Add feeder service '{feeder_service_name}' to database")
port_call_manager.add_service_that_calls_terminal(
    vehicle_type=conflowgen.ModeOfTransport.feeder,
    service_name=feeder_service_name,
    vehicle_arrives_at=datetime.date(2021, 7, 9),
    vehicle_arrives_at_time=datetime.time(11),
    average_vehicle_capacity=800,
    average_inbound_container_volume=100,
    next_destinations=[
        ("DEBRV", 0.4),  # 50% of the containers (in boxes) go here...
        ("RULED", 0.6)   # and the other 50% of the containers (in boxes) go here.
    ]
)

train_service_name = "JR03A"
logger.info(f"Add train service '{train_service_name}' to database")
port_call_manager.add_service_that_calls_terminal(
    vehicle_type=conflowgen.ModeOfTransport.train,
    service_name=train_service_name,
    vehicle_arrives_at=datetime.date(2021, 7, 12),
    vehicle_arrives_at_time=datetime.time(17),
    average_vehicle_capacity=90,
    average_inbound_container_volume=90,
    next_destinations=None  # Here we don't have containers that need to be grouped by destination
)

deep_sea_service_name = "LX050"
logger.info(f"Add deep sea vessel service '{deep_sea_service_name}' to database")
port_call_manager.add_service_that_calls_terminal(
    vehicle_type=conflowgen.ModeOfTransport.deep_sea_vessel,
    service_name=deep_sea_service_name,
    vehicle_arrives_at=datetime.date(2021, 7, 10),
    vehicle_arrives_at_time=datetime.time(19),
    average_vehicle_capacity=16000,
    average_inbound_container_volume=150,  # for faster demo
    next_destinations=[
        ("ZADUR", 0.3),  # 30% of the containers (in boxes) go here...
        ("CNSHG", 0.7)   # and the other 70% of the containers (in boxes) go here.
    ]
)

###
# Now, all schedules and input distributions are set up - no further inputs are required
###

logger.info("Preview the results with some light-weight approaches.")

conflowgen.run_all_previews(
    as_graph=with_visuals
)

logger.info("Generate all fleets with all vehicles. This is the core of the whole project.")
container_flow_generation_manager.generate()

logger.info("The container flow data have been generated, run post-hoc analyses on them")

conflowgen.run_all_analyses(
    as_graph=with_visuals
)

logger.info("For a better understanding of the data, it is advised to study the logs and compare the preview with the "
            "analysis results")

logger.info("Start data export...")

# Export important entries from SQL to CSV so that it can be further processed, e.g., by a simulation software
export_container_flow_manager = conflowgen.ExportContainerFlowManager()
export_folder_name = "demo-poc--" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "--").split(".")[0]
export_container_flow_manager.export(
    folder_name=export_folder_name,
    path_to_export_folder=os.path.join(this_dir, "export"),
    file_format=conflowgen.ExportFileFormat.csv
)

# Gracefully close everything
database_chooser.close_current_connection()
logger.info(f"ConFlowGen {conflowgen.__version__} from {conflowgen.__file__} was used.")
try:
    last_git_commit = str(subprocess.check_output(["git", "log", "-1"]).strip())  # nosec B607
    logger.info("Used git commit: " + last_git_commit[2:-1])
except:  # pylint: disable=bare-except
    logger.debug("The last git commit of this repository could not be retrieved, skip this.")
logger.info("Demo 'demo_poc' finished successfully.")
