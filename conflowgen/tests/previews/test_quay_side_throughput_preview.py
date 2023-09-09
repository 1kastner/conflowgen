import unittest
import datetime

from conflowgen import ModeOfTransport, ContainerLength
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.previews.quay_side_throughput_preview import QuaySideThroughputPreview
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestQuaySideThroughputPreview(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            ModeOfTransportDistribution,
            ContainerLengthDistribution,
            ContainerFlowGenerationProperties,
            TruckArrivalDistribution
        ])
        now = datetime.datetime.now()
        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions({
            ModeOfTransport.truck: {
                ModeOfTransport.truck: 0.1,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.4,
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
        ContainerLengthDistributionRepository().set_distribution({
            ContainerLength.twenty_feet: 0,
            ContainerLength.forty_feet: 1,
            ContainerLength.forty_five_feet: 0,
            ContainerLength.other: 0
        })
        ContainerFlowGenerationProperties.create(
            start_date=now,
            end_date=now + datetime.timedelta(weeks=2)
        )  # mostly use default values

        self.preview = QuaySideThroughputPreview(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.0
        )

    def test_empty(self):
        volume = self.preview.get_quay_side_throughput()
        volume_i = volume.inbound
        volume_o = volume.outbound
        volume_i_teu = volume_i.teu
        volume_i_box = volume_i.containers
        volume_o_teu = volume_o.teu
        volume_o_box = volume_o.containers
        self.assertEqual(volume_i_teu, 0)
        self.assertEqual(volume_i_box, 0)
        self.assertEqual(volume_o_teu, 0)
        self.assertEqual(volume_o_box, 0)

    def test_one_feeder(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=150,
            vehicle_arrives_every_k_days=-1
        )
        volume = self.preview.get_quay_side_throughput()
        volume_i = volume.inbound
        volume_o = volume.outbound
        volume_i_teu = volume_i.teu
        volume_i_box = volume_i.containers
        volume_o_teu = volume_o.teu
        volume_o_box = volume_o.containers
        self.assertAlmostEqual(volume_i_teu, 150)
        self.assertAlmostEqual(volume_i_box, 75)
        self.assertAlmostEqual(volume_o_teu, 72)
        self.assertAlmostEqual(volume_o_box, 36)
