import unittest

from conflowgen.database_connection.create_tables import create_tables
from conflowgen.domain_models.distribution_seeders.seed_database import seed_all_distributions
from conflowgen.posthoc_analyses import run_all_posthoc_analyses
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db

EMPTY_OUTPUT = [
    'INFO:conflowgen:Run all post-hoc analyses on the synthetically generated '
    'data',
    'INFO:conflowgen:Analysis report: '
    'InboundAndOutboundVehicleCapacityAnalysisReport',
    'INFO:conflowgen:Analyze the vehicle capacity by vehicle type for the inbound '
    'and outbound\n'
    'journeys and check for the maximum capacity of each vehicle type. If e.g. '
    'for\n'
    "the vehicle type 'feeder' the maximum outbound capacity is used up, most "
    'likely\n'
    'there are more vehicles that deliver containers destined for feeder vessels '
    'than\n'
    'there are feeder vessels planned during the period of data generation '
    '(between\n'
    '`start_date` and `end_date`).',
    'INFO:conflowgen:\n'
    'vehicle type    inbound capacity outbound actual capacity outbound max '
    'capacity\n'
    'deep sea vessel              0.0                      0.0                   '
    '0.0\n'
    'feeder                       0.0                      0.0                   '
    '0.0\n'
    'barge                        0.0                      0.0                   '
    '0.0\n'
    'train                        0.0                      0.0                   '
    '0.0\n'
    'truck                        0.0                      0.0                  '
    '-1.0\n'
    '(rounding errors might exist)\n',
    'INFO:conflowgen:Analysis report: ContainerFlowByVehicleTypeAnalysisReport',
    'INFO:conflowgen:Analyze how many containers were delivered by which vehicle '
    'type and how their\n'
    'journey continued. The analysis pairs the inbound and outbound journey for '
    'each\n'
    'container.',
    'INFO:conflowgen:\n'
    'vehicle type (from) vehicle type (to) transported capacity (in TEU)\n'
    'deep sea vessel     deep sea vessel                             0.0\n'
    'deep sea vessel     feeder                                      0.0\n'
    'deep sea vessel     barge                                       0.0\n'
    'deep sea vessel     train                                       0.0\n'
    'deep sea vessel     truck                                       0.0\n'
    'feeder              deep sea vessel                             0.0\n'
    'feeder              feeder                                      0.0\n'
    'feeder              barge                                       0.0\n'
    'feeder              train                                       0.0\n'
    'feeder              truck                                       0.0\n'
    'barge               deep sea vessel                             0.0\n'
    'barge               feeder                                      0.0\n'
    'barge               barge                                       0.0\n'
    'barge               train                                       0.0\n'
    'barge               truck                                       0.0\n'
    'train               deep sea vessel                             0.0\n'
    'train               feeder                                      0.0\n'
    'train               barge                                       0.0\n'
    'train               train                                       0.0\n'
    'train               truck                                       0.0\n'
    'truck               deep sea vessel                             0.0\n'
    'truck               feeder                                      0.0\n'
    'truck               barge                                       0.0\n'
    'truck               train                                       0.0\n'
    'truck               truck                                       0.0\n'
    '(rounding errors might exist)\n',
    'INFO:conflowgen:Analysis report: '
    'ContainerFlowAdjustmentByVehicleTypeAnalysisReport',
    'INFO:conflowgen:Analyze how many containers needed to change their initial '
    'container type. When\n'
    'containers are generated, in order to obey the maximum dwell time, the '
    'vehicle\n'
    'type that is used for onward transportation might change. The initial '
    'outbound\n'
    'vehicle type is the vehicle type that is drawn randomly for a container at '
    'the\n'
    'time of generation. The adjusted vehicle type is the vehicle type that is '
    'drawn\n'
    'in case no vehicle of the initial outbound vehicle type is left within the\n'
    'maximum dwell time.',
    'INFO:conflowgen:\n'
    'vehicle type (initial) vehicle type (adjusted) transported capacity (in TEU) '
    'transported capacity (in containers)\n'
    'deep sea vessel        deep sea vessel                                   '
    '0.0                                    0\n'
    'deep sea vessel        feeder                                            '
    '0.0                                    0\n'
    'deep sea vessel        barge                                             '
    '0.0                                    0\n'
    'deep sea vessel        train                                             '
    '0.0                                    0\n'
    'deep sea vessel        truck                                             '
    '0.0                                    0\n'
    'feeder                 deep sea vessel                                   '
    '0.0                                    0\n'
    'feeder                 feeder                                            '
    '0.0                                    0\n'
    'feeder                 barge                                             '
    '0.0                                    0\n'
    'feeder                 train                                             '
    '0.0                                    0\n'
    'feeder                 truck                                             '
    '0.0                                    0\n'
    'barge                  deep sea vessel                                   '
    '0.0                                    0\n'
    'barge                  feeder                                            '
    '0.0                                    0\n'
    'barge                  barge                                             '
    '0.0                                    0\n'
    'barge                  train                                             '
    '0.0                                    0\n'
    'barge                  truck                                             '
    '0.0                                    0\n'
    'train                  deep sea vessel                                   '
    '0.0                                    0\n'
    'train                  feeder                                            '
    '0.0                                    0\n'
    'train                  barge                                             '
    '0.0                                    0\n'
    'train                  train                                             '
    '0.0                                    0\n'
    'train                  truck                                             '
    '0.0                                    0\n'
    'truck                  deep sea vessel                                   '
    '0.0                                    0\n'
    'truck                  feeder                                            '
    '0.0                                    0\n'
    'truck                  barge                                             '
    '0.0                                    0\n'
    'truck                  train                                             '
    '0.0                                    0\n'
    'truck                  truck                                             '
    '0.0                                    0\n'
    '(rounding errors might exist)\n',
    'INFO:conflowgen:Analysis report: '
    'ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport',
    'INFO:conflowgen:Analyse whether a container needed to change its vehicle '
    'type for the outbound\n'
    'journey and if that was the case, how many times which vehicle type was '
    'chosen\n'
    'in order to not exceed the maximum dwell time.',
    'INFO:conflowgen:\n'
    '                             Capacity in TEU\n'
    'vehicle type unchanged:      0.0        (-%)\n'
    'changed to deep sea vessel:  0.0        (-%)\n'
    'changed to feeder:           0.0        (-%)\n'
    'changed to barge:            0.0        (-%)\n'
    'changed to train:            0.0        (-%)\n'
    'changed to truck:            0.0        (-%)\n'
    '(rounding errors might exist)\n',
    'INFO:conflowgen:Analysis report: ModalSplitAnalysisReport',
    'INFO:conflowgen:Analyze the amount of containers dedicated for or coming '
    'from the hinterland\n'
    'versus the amount of containers that are transshipment.',
    'INFO:conflowgen:\n'
    'Transshipment share\n'
    'transshipment proportion (in TEU):       0.00 (-%)\n'
    'hinterland proportion (in TEU):          0.00 (-%)\n'
    '\n'
    'Inbound modal split\n'
    'truck proportion (in TEU):        0.0 (-%)\n'
    'barge proportion (in TEU):        0.0 (-%)\n'
    'train proportion (in TEU):        0.0 (-%)\n'
    '\n'
    'Outbound modal split\n'
    'truck proportion (in TEU):        0.0 (-%)\n'
    'barge proportion (in TEU):        0.0 (-%)\n'
    'train proportion (in TEU):        0.0 (-%)\n'
    '\n'
    'Absolute modal split (both inbound and outbound)\n'
    'truck proportion (in TEU):        0.0 (-%)\n'
    'barge proportion (in TEU):        0.0 (-%)\n'
    'train proportion (in TEU):        0.0 (-%)\n'
    '(rounding errors might exist)\n',
    'INFO:conflowgen:Analysis report: QuaySideThroughputAnalysisReport',
    'INFO:conflowgen:Analyse the throughput at the quay side. In the text version '
    'of the report, only\n'
    'the statistics are reported. In the visual version of the report, the time\n'
    'series is plotted.',
    'INFO:conflowgen:\n'
    '                                     (reported in boxes)\n'
    'maximum weekly quay side throughput:                   0\n'
    'average weekly quay side throughput:                 0.0\n'
    'standard deviation:                                 -1.0\n'
    'maximum daily quay side throughput:                  0.0\n'
    'average daily quay side throughput:                  0.0\n'
    'maximum hourly quay side throughput:                 0.0\n'
    'average hourly quay side throughput:                 0.0\n'
    '(daily and hourly values are simply scaled weekly values, rounding errors '
    'might exist)\n',
    'INFO:conflowgen:Analysis report: TruckGateThroughputAnalysisReport',
    'INFO:conflowgen:Analyze the trucks entering through the truck gate at each '
    'hour. Based on this,\n'
    'the required truck gate capacity in containers boxes can be deduced. In the '
    'text\n'
    'version of the report, only the statistics are reported. In the visual '
    'version\n'
    'of the report, the time series is plotted.',
    'INFO:conflowgen:\n'
    '                                     (reported in boxes)\n'
    'maximum hourly truck gate throughput:                  0\n'
    'average hourly truck gate throughput:                0.0\n'
    'standard deviation:                                 -1.0\n'
    '(rounding errors might exist)\n',
    'INFO:conflowgen:Analysis report: YardCapacityAnalysisReport',
    'INFO:conflowgen:Analyse the used capacity in the yard. For each hour, the '
    'containers entering\n'
    'and leaving the yard are checked. Based on this, the required yard capacity '
    'in\n'
    'TEU can be deduced. In the text version of the report, only the statistics '
    'are\n'
    'reported. In the visual version of the report, the time series is plotted.',
    'INFO:conflowgen:\n'
    '                                     (reported in TEU)\n'
    'maximum used yard capacity:                        0.0\n'
    'average used yard capacity:                        0.0\n'
    'standard deviation:                               -1.0\n'
    'maximum used yard capacity (laden):                0.0\n'
    'average used yard capacity (laden):                0.0\n'
    'standard deviation (laden):                       -1.0\n'
    '(rounding errors might exist)\n',
    'INFO:conflowgen:All post-hoc analyses have been run.']


class TestRunAllPosthocAnalyses(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        create_tables(self.sqlite_db)
        seed_all_distributions()

    def test_with_no_data(self):
        with self.assertLogs('conflowgen', level='INFO') as cm:
            run_all_posthoc_analyses()
        self.maxDiff = None
        self.assertEqual(cm.output, EMPTY_OUTPUT)
