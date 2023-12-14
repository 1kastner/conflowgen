import datetime
import unittest

from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.api.container_length_distribution_manager import ContainerLengthDistributionManager
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.previews.container_flow_by_vehicle_type_preview import \
    ContainerFlowByVehicleTypePreview
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowByVehicleTypePreview(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            ModeOfTransportDistribution,
            ContainerLengthDistribution
        ])
        now = datetime.datetime.now()

        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions({
            ModeOfTransport.truck: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.train: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.barge: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.feeder: {
                ModeOfTransport.truck: 0.2,
                ModeOfTransport.train: 0.4,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            },
            ModeOfTransport.deep_sea_vessel: {
                ModeOfTransport.truck: 0.2,
                ModeOfTransport.train: 0.4,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            }
        })

        container_length_manager = ContainerLengthDistributionManager()
        container_length_manager.set_container_length_distribution(  # Set default container length distribution
            {
                ContainerLength.other: 0.001,
                ContainerLength.twenty_feet: 0.4,
                ContainerLength.forty_feet: 0.57,
                ContainerLength.forty_five_feet: 0.029
            }
        )

        self.preview = ContainerFlowByVehicleTypePreview(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.2
        )

    def test_with_no_schedules(self):
        """If no schedules are provided, no capacity is needed"""
        empty_flow = self.preview.get_inbound_to_outbound_flow()
        self.assertSetEqual(set(ModeOfTransport), set(empty_flow.keys()))
        for mode_of_transport_from in ModeOfTransport:
            flow_from_vehicle_type = empty_flow[mode_of_transport_from]
            self.assertSetEqual(set(ModeOfTransport), set(flow_from_vehicle_type.keys()))
            for mode_of_transport_to in ModeOfTransport:
                capacity_in_teu = flow_from_vehicle_type[mode_of_transport_to]
                self.assertEqual(capacity_in_teu, 0, f"Expect no flow from {mode_of_transport_from} to "
                                                     f"{mode_of_transport_to} but it was {capacity_in_teu}")

    def test_with_single_arrival_schedules(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()

        flow_with_one_entry = self.preview.get_inbound_to_outbound_flow()
        self.assertSetEqual(set(ModeOfTransport), set(flow_with_one_entry.keys()))
        uninvolved_vehicles = set(ModeOfTransport) - {ModeOfTransport.feeder, ModeOfTransport.truck}
        for mode_of_transport_from in uninvolved_vehicles:
            flow_from_vehicle_type = flow_with_one_entry[mode_of_transport_from]
            self.assertSetEqual(set(ModeOfTransport), set(flow_from_vehicle_type.keys()))
            for mode_of_transport_to in ModeOfTransport:
                capacity_in_teu = flow_from_vehicle_type[mode_of_transport_to]
                self.assertEqual(capacity_in_teu, 0, f"Expect no flow from {mode_of_transport_from} to "
                                                     f"{mode_of_transport_to} but it was {capacity_in_teu}")
        flow_to_feeder = flow_with_one_entry[ModeOfTransport.feeder]
        for mode_of_transport_to in (set(ModeOfTransport) - {ModeOfTransport.barge}):
            transported_capacity = flow_to_feeder[mode_of_transport_to]
            self.assertGreater(transported_capacity, 0)
        flow_from_truck_to_feeder = flow_with_one_entry[ModeOfTransport.truck][ModeOfTransport.feeder]
        self.assertGreater(flow_from_truck_to_feeder, 0, "Some containers must be delivered by truck for the feeder")
