"""
The intention of this script is to provide a demonstration of how ConFlowGen is supposed to be used as a library.
It is, by design, a stateful library that persists all input in an SQL database format to enable reproducibility.
The intention of this demo is further explained in the logs it generated.
"""

import datetime
import os.path
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(sys.modules[__name__].__file__),
            os.pardir,
            os.pardir
        )
    )
)

from conflowgen import ContainerFlowGenerationManager
from conflowgen import ModeOfTransport
from conflowgen import PortCallManager
from conflowgen import ExportFileFormat
from conflowgen import ExportContainerFlowManager
from conflowgen import DatabaseChooser
from conflowgen import setup_logger
from conflowgen import InboundAndOutboundVehicleCapacityPreviewReport
from conflowgen import ContainerFlowByVehicleTypePreviewReport
from conflowgen import VehicleCapacityExceededPreviewReport
from conflowgen import ModalSplitPreviewReport
from conflowgen import InboundAndOutboundVehicleCapacityAnalysisReport
from conflowgen import ContainerFlowByVehicleTypeAnalysisReport
from conflowgen import ModalSplitAnalysisReport
from conflowgen import ContainerFlowAdjustmentByVehicleTypeAnalysisReport
from conflowgen import ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport

# Start logging
logger = setup_logger()

logger.info("""####
## Demo Proof of Concept
####
This demo is based on some example data and is meant to show the basic functionality. For a slightly more realistic
example, please check out `demo_DEHAM_CTA.py`. However, computing those numbers also takes longer than quickly running
this small example.
""")

# Pick database
database_chooser = DatabaseChooser()
demo_file_name = "demo_poc.sqlite"
if demo_file_name in database_chooser.list_all_sqlite_databases():
    database_chooser.load_existing_sqlite_database(demo_file_name)
else:
    database_chooser.create_new_sqlite_database(demo_file_name)


# Set settings
container_flow_generation_manager = ContainerFlowGenerationManager()
container_flow_generation_manager.set_properties(
    name="Demo file",
    start_date=datetime.datetime.now().date(),
    end_date=datetime.datetime.now().date() + datetime.timedelta(days=21)
)


# Add vehicles that frequently visit the terminal.

port_call_manager = PortCallManager()
feeder_service_name = "LX050"
if not port_call_manager.get_schedule(feeder_service_name, vehicle_type=ModeOfTransport.feeder):
    logger.info(f"Add feeder service '{feeder_service_name}' to database")
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=ModeOfTransport.feeder,
        service_name=feeder_service_name,
        vehicle_arrives_at=datetime.date(2021, 7, 9),
        vehicle_arrives_at_time=datetime.time(11),
        average_vehicle_capacity=800,
        average_moved_capacity=100,
        next_destinations=[
            ("DEBRV", 0.4),  # 50% of the containers go here...
            ("RULED", 0.6)   # and the other 50% of the containers go here.
        ]
    )
else:
    logger.info(f"Feeder service '{feeder_service_name}' already exists")

train_service_name = "JR03A"
if not port_call_manager.get_schedule(train_service_name, vehicle_type=ModeOfTransport.train):
    logger.info(f"Add train service '{train_service_name}' to database")
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=ModeOfTransport.train,
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
if not port_call_manager.get_schedule(deep_sea_service_name, vehicle_type=ModeOfTransport.deep_sea_vessel):
    logger.info(f"Add deep sea vessel service '{deep_sea_service_name}' to database")
    port_call_manager.add_large_scheduled_vehicle(
        vehicle_type=ModeOfTransport.deep_sea_vessel,
        service_name=deep_sea_service_name,
        vehicle_arrives_at=datetime.date(2021, 7, 10),
        vehicle_arrives_at_time=datetime.time(19),
        average_vehicle_capacity=16000,
        average_moved_capacity=150,  # for faster demo
        next_destinations=[
            ("ZADUR", 0.3),  # 30% of the containers go here...
            ("CNSHG", 0.7)   # and the other 70% of the containers go here.
        ]
    )
else:
    logger.info(f"Deep sea service '{deep_sea_service_name}' already exists")

logger.info("Generating reports on the input data (preview of container flow to generate)")
inbound_and_outbound_vehicle_capacity_preview_report = InboundAndOutboundVehicleCapacityPreviewReport()
report = inbound_and_outbound_vehicle_capacity_preview_report.get_report_as_text()
logger.info("Inbound and outbound traffic: ")
logger.info(report)

container_flow_by_vehicle_type_preview_report = ContainerFlowByVehicleTypePreviewReport()
report = container_flow_by_vehicle_type_preview_report.get_report_as_text()
logger.info("Container flow between vehicle types as defined by schedules and distributions: ")
logger.info(report)

modal_split_preview_report = ModalSplitPreviewReport()
report = modal_split_preview_report.get_report_as_text()
logger.info("The same container flow expressed in terms of transshipment and modal split for the hinterland: ")
logger.info(report)

vehicle_capacity_exceeded_preview_report = VehicleCapacityExceededPreviewReport()
report = vehicle_capacity_exceeded_preview_report.get_report_as_text()
logger.info("Consequences of container flow for outgoing vehicles: ")
logger.info(report)

logger.info("All reports on the input data have been generated")

# Generate all fleets with all vehicles. This is the core of the whole code.
container_flow_generation_manager.generate()

logger.info("The container flow data have been generated, run posthoc analyses on them")

logger.info("Analyze the amount of containers being delivered at the terminal and being picked by by mode of transport")
inbound_and_outbound_vehicle_capacity_analysis_report = InboundAndOutboundVehicleCapacityAnalysisReport()
report = inbound_and_outbound_vehicle_capacity_analysis_report.get_report_as_text()
logger.info(report)

logger.info("Analyze the amount of containers being delivered by one vehicle and being picked up by another vehicle "
            "(by vehicle type)")
container_flow_by_vehicle_type_analysis_report = ContainerFlowByVehicleTypeAnalysisReport()
report = container_flow_by_vehicle_type_analysis_report.get_report_as_text()
logger.info(report)

logger.info("Reformat same data to show the transshipment share and modal split in the hinterland")
modal_split_analysis_report = ModalSplitAnalysisReport()
report = modal_split_analysis_report.get_report_as_text()
logger.info(report)

logger.info("Analyze the amount of containers which require an adjustment in mode of transport because they could not "
            "leave the container terminal within the maximum container dwell time otherwise. If the initial type "
            "and the adjusted type are identical, no adjustment has taken place. These numbers are just reported "
            "for reference.")
container_flow_adjustment_by_vehicle_type_analysis_report = ContainerFlowAdjustmentByVehicleTypeAnalysisReport()
report = container_flow_adjustment_by_vehicle_type_analysis_report.get_report_as_text()
logger.info(report)

logger.info("Summarize the previous figures of how containers have been redirected to other vehicle types")
container_flow_adjustment_by_vehicle_type_analysis_summary = ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport()
report = container_flow_adjustment_by_vehicle_type_analysis_summary.get_report_as_text()
logger.info(report)

logger.info("All posthoc analyses have been run.")

logger.info("For a better understanding of the data, it is advised to study the logs and compare the preview with the "
            "posthoc analysis results")

logger.info("Start data export...")

# Export important entries from SQL to CSV so that it can be further processed, e.g. by a simulation software
export_container_flow_manager = ExportContainerFlowManager()
export_container_flow_manager.export(
    folder_name="demo-poc--" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "--").split(".")[0],
    file_format=ExportFileFormat.CSV
)

# Gracefully close everything
database_chooser.close_current_connection()
logger.info("Demo 'demo_poc' finished successfully.")
