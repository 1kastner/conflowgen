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
import sys

try:
    import conflowgen
    print(f"Importing ConFlowGen version {conflowgen.__version__}")
except ImportError:
    print("Please first install conflowgen as a library")
    sys.exit()

# Start logging
logger = conflowgen.setup_logger()
logger.info(__doc__)

# Pick database
database_chooser = conflowgen.DatabaseChooser()
demo_file_name = "demo_poc.sqlite"
if demo_file_name in database_chooser.list_all_sqlite_databases():
    database_chooser.load_existing_sqlite_database(demo_file_name)
else:
    database_chooser.create_new_sqlite_database(demo_file_name)


# Set settings
container_flow_generation_manager = conflowgen.ContainerFlowGenerationManager()
container_flow_generation_manager.set_properties(
    name="Demo file",
    start_date=datetime.datetime.now().date(),
    end_date=datetime.datetime.now().date() + datetime.timedelta(days=21)
)


# Add vehicles that frequently visit the terminal.

port_call_manager = conflowgen.PortCallManager()
feeder_service_name = "LX050"
if not port_call_manager.has_schedule(feeder_service_name, vehicle_type=conflowgen.ModeOfTransport.feeder):
    logger.info(f"Add feeder service '{feeder_service_name}' to database")
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.feeder,
        service_name=feeder_service_name,
        vehicle_arrives_at=datetime.date(2021, 7, 9),
        vehicle_arrives_at_time=datetime.time(11),
        average_vehicle_capacity=800,
        average_moved_capacity=100,
        next_destinations=[
            ("DEBRV", 0.4),  # 50% of the containers (in boxes) go here...
            ("RULED", 0.6)   # and the other 50% of the containers (in boxes) go here.
        ]
    )
else:
    logger.info(f"Feeder service '{feeder_service_name}' already exists")

train_service_name = "JR03A"
if not port_call_manager.has_schedule(train_service_name, vehicle_type=conflowgen.ModeOfTransport.train):
    logger.info(f"Add train service '{train_service_name}' to database")
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.train,
        service_name=train_service_name,
        vehicle_arrives_at=datetime.date(2021, 7, 12),
        vehicle_arrives_at_time=datetime.time(17),
        average_vehicle_capacity=90,
        average_moved_capacity=90,
        next_destinations=None  # Here we don't have containers that need to be grouped by destination
    )
else:
    logger.info(f"Train service '{train_service_name}' already exists")

deep_sea_service_name = "LX050"
if not port_call_manager.has_schedule(deep_sea_service_name, vehicle_type=conflowgen.ModeOfTransport.deep_sea_vessel):
    logger.info(f"Add deep sea vessel service '{deep_sea_service_name}' to database")
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=conflowgen.ModeOfTransport.deep_sea_vessel,
        service_name=deep_sea_service_name,
        vehicle_arrives_at=datetime.date(2021, 7, 10),
        vehicle_arrives_at_time=datetime.time(19),
        average_vehicle_capacity=16000,
        average_moved_capacity=150,  # for faster demo
        next_destinations=[
            ("ZADUR", 0.3),  # 30% of the containers (in boxes) go here...
            ("CNSHG", 0.7)   # and the other 70% of the containers (in boxes) go here.
        ]
    )
else:
    logger.info(f"Deep sea service '{deep_sea_service_name}' already exists")

###
# Now, all schedules and input distributions are set up - no further inputs are required
###

logger.info("Preview the results with some light-weight approaches.")

conflowgen.run_all_previews()

logger.info("Generate all fleets with all vehicles. This is the core of the whole project.")
container_flow_generation_manager.generate()

logger.info("The container flow data have been generated, run post-hoc analyses on them")

conflowgen.run_all_analyses()

logger.info("For a better understanding of the data, it is advised to study the logs and compare the preview with the "
            "post-hoc analysis results")

logger.info("Start data export...")

# Export important entries from SQL to CSV so that it can be further processed, e.g. by a simulation software
export_container_flow_manager = conflowgen.ExportContainerFlowManager()
export_folder_name = "demo-poc--" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "--").split(".")[0]
export_container_flow_manager.export(
    folder_name=export_folder_name + "-csv",
    file_format=conflowgen.ExportFileFormat.csv
)
export_container_flow_manager.export(
    folder_name=export_folder_name + "-xlsx",
    file_format=conflowgen.ExportFileFormat.xlsx
)

# Gracefully close everything
database_chooser.close_current_connection()
logger.info("Demo 'demo_poc' finished successfully.")
