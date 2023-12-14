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
from conflowgen.previews.modal_split_preview import ModalSplitPreview
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestModalSplitPreview__get_modal_split_for_hinterland(unittest.TestCase):  # pylint: disable=invalid-name
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

        self.preview = ModalSplitPreview(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.2
        )

    def test_with_no_schedules(self):
        """If no schedules are provided, this should not fail"""
        empty_split = self.preview.get_modal_split_for_hinterland(True, True)
        self.assertEqual(empty_split.truck_capacity, 0)
        self.assertEqual(empty_split.barge_capacity, 0)
        self.assertEqual(empty_split.train_capacity, 0)

    def test_with_single_arrival_schedules(self):
        """inbound is 300 TEU by feeder and thus, outbound we have:
        - 300 TEU * 20% trucks -> 60 TEU, then 60 TEU are also generated to be delivered by truck to the vessels
        - 300 TEU * 10% barge -> 30 TEU
        - 300 TEU * 40% train -> 120 TEU
        """
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
        actual_split = self.preview.get_modal_split_for_hinterland(True, True)
        self.assertAlmostEqual(actual_split.truck_capacity, 120)
        self.assertAlmostEqual(actual_split.barge_capacity, 30)
        self.assertAlmostEqual(actual_split.train_capacity, 120)
