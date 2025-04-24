import datetime
import os
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

with_visuals = False
if len(sys.argv) > 2:
    if sys.argv[2] == "--with-visuals":
        with_visuals = True
# The seed of x=1 guarantees that the same traffic data is generated as input data in this script. However, it does not
# affect the container generation or the assignment of containers to vehicles.
seeded_random = random.Random(x=1)

# get the current working directory
current_dir = os.getcwd()
# Define the relative path to the csv file
import_salalah_dir = os.path.join(
    current_dir,
    "data",
    "Salalah",
)

df = pd.read_csv(
    os.path.join(
        import_salalah_dir,
        "Salalah_portcall1.csv"
    )
)
# Classify vessels based on capacity and add a new column "Vessel Type"
df['Vessel Type'] = df['Capacity - Teu'].apply(lambda x: 'feeder' if x <= 3000 else 'deep_sea_vessel')

# Start logging
logger = conflowgen.setup_logger()
logger.info(__doc__)

# Pick database
database_chooser = conflowgen.DatabaseChooser(
    sqlite_databases_directory=os.path.join(current_dir, "databases")
)

demo_file_name = "demo_Salalah_with_transshipment.sqlite"
database_chooser.create_new_sqlite_database(
    demo_file_name,
    assume_tas=True,
    overwrite=True
)
# Set settings
container_flow_generation_manager = conflowgen.ContainerFlowGenerationManager()
container_flow_generation_manager.set_properties(
    name=f"Salalah April_May 2024",
    start_date=datetime.datetime(2024, 4, 16),
    end_date=datetime.datetime(2024, 5, 15),
    ramp_up_period=datetime.timedelta(days=7),
    ramp_down_period=datetime.timedelta(days=7),
)

# Set some general assumptions regarding the container properties
container_length_distribution_manager = conflowgen.ContainerLengthDistributionManager()
container_length_distribution_manager.set_container_length_distribution({
    conflowgen.ContainerLength.twenty_feet: 0.40,
    conflowgen.ContainerLength.forty_feet: 0.60,
    conflowgen.ContainerLength.forty_five_feet: 0,
    conflowgen.ContainerLength.other: 0
})
mode_of_transport_distribution_manager = conflowgen.ModeOfTransportDistributionManager()
mode_of_transport_distribution = mode_of_transport_distribution_manager.get_mode_of_transport_distribution()

# Modify the distribution

mode_of_transport_distribution[conflowgen.ModeOfTransport.feeder] = {
    conflowgen.ModeOfTransport.truck: 13.0,
    conflowgen.ModeOfTransport.train: 0,
    conflowgen.ModeOfTransport.barge: 0,
    conflowgen.ModeOfTransport.feeder: 0,
    conflowgen.ModeOfTransport.deep_sea_vessel: 87.0
}

mode_of_transport_distribution[conflowgen.ModeOfTransport.deep_sea_vessel] = {
    conflowgen.ModeOfTransport.truck: 13.0,
    conflowgen.ModeOfTransport.train: 0,
    conflowgen.ModeOfTransport.barge: 0,
    conflowgen.ModeOfTransport.feeder: 34.8,
    conflowgen.ModeOfTransport.deep_sea_vessel: 52.2
}

mode_of_transport_distribution[conflowgen.ModeOfTransport.truck] = {
    conflowgen.ModeOfTransport.truck: 0,
    conflowgen.ModeOfTransport.train: 0,
    conflowgen.ModeOfTransport.barge: 0,
    conflowgen.ModeOfTransport.feeder: 25,
    conflowgen.ModeOfTransport.deep_sea_vessel: 75
}

storage_manager = conflowgen.StorageRequirementDistributionManager()

storage_manager.set_storage_requirement_distribution(
    {
        conflowgen.ContainerLength.twenty_feet: {
            conflowgen.StorageRequirement.empty: 0.23,
            conflowgen.StorageRequirement.standard: 0.77,
            conflowgen.StorageRequirement.reefer: 0,
            conflowgen.StorageRequirement.dangerous_goods: 0,
        },
        conflowgen.ContainerLength.forty_feet: {
            conflowgen.StorageRequirement.empty: 0.23,
            conflowgen.StorageRequirement.standard: 0.77,
            conflowgen.StorageRequirement.reefer: 0,
            conflowgen.StorageRequirement.dangerous_goods: 0,
        },
        conflowgen.ContainerLength.forty_five_feet: {
            conflowgen.StorageRequirement.empty: 1,
            conflowgen.StorageRequirement.standard: 1,
            conflowgen.StorageRequirement.reefer: 1,
            conflowgen.StorageRequirement.dangerous_goods: 1,
        },
        conflowgen.ContainerLength.other: {
            conflowgen.StorageRequirement.empty: 1,
            conflowgen.StorageRequirement.standard: 1,
            conflowgen.StorageRequirement.reefer: 1,
            conflowgen.StorageRequirement.dangerous_goods: 1,
        },
    }
)

moved_inbound_volume_by_feeder = 0
moved_inbound_volume_by_deep_sea_vessel = 0

name_counter = {
    conflowgen.ModeOfTransport.deep_sea_vessel: {},
    conflowgen.ModeOfTransport.feeder: {}
}
port_call_manager = conflowgen.PortCallManager()
for index, row in df.iterrows():
    planned_arrival = pd.to_datetime(row["Dock Timestamp"])
    vessel_name = row["Vessel Name"]
    port_call_size = row["Estimated Port Call Size"]
    vessel_type = row["Vessel Type"]
    capacity = row["Capacity - Teu"]

    casted_vessel_type = {
        "deep_sea_vessel": conflowgen.ModeOfTransport.deep_sea_vessel,
        "feeder": conflowgen.ModeOfTransport.feeder
    }[vessel_type]

    name_counter[casted_vessel_type][vessel_name] = name_counter[casted_vessel_type].get(vessel_name, 0) + 1

    if name_counter[casted_vessel_type][vessel_name] > 1:
        vessel_name += "_" + str(name_counter[casted_vessel_type][vessel_name])

    containers_moved_on_journey = port_call_size / 2
    if casted_vessel_type == conflowgen.ModeOfTransport.feeder:
        moved_inbound_volume_by_feeder += containers_moved_on_journey
    elif casted_vessel_type == conflowgen.ModeOfTransport.deep_sea_vessel:
        moved_inbound_volume_by_deep_sea_vessel += containers_moved_on_journey
    else:
        raise Exception(f"{vessel_type=}")

    port_call_manager.add_vehicle(
        vehicle_type=casted_vessel_type,
        service_name=vessel_name,
        vehicle_arrives_at=planned_arrival.date(),
        vehicle_arrives_at_time=planned_arrival.time(),
        vehicle_capacity=capacity,
        inbound_container_volume=containers_moved_on_journey,

    )

estimated_total_moved_capacity_on_seaside = (moved_inbound_volume_by_feeder + moved_inbound_volume_by_deep_sea_vessel)*2
print(estimated_total_moved_capacity_on_seaside)

container_flow_generation_manager.generate(
    overwrite=False
)

# Export important entries from SQL to CSV so that it can be further processed, e.g., by a simulation software
export_container_flow_manager = conflowgen.ExportContainerFlowManager()
export_container_flow_manager.export(
    folder_name="Salalah" + "_" + "__" + str(datetime.datetime.now()).replace(":", "-").replace(" ", "--").split(".")[
        0],
    path_to_export_folder=os.path.join("ConFlowGen_data", "LogMS2024_csv", "Salalah"),
    file_format=conflowgen.ExportFileFormat.csv
)

# Gracefully close everything
database_chooser.close_current_connection()
