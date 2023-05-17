import datetime

from conflowgen import ModeOfTransport, ContainerLength, TruckArrivalDistributionManager
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.previews.truck_gate_throughput_preview_report import TruckGateThroughputPreviewReport
from conflowgen.tests.autoclose_matplotlib import UnitTestCaseWithMatplotlib
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckGateThroughputPreviewReport(UnitTestCaseWithMatplotlib):

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
            ContainerLength.twenty_feet: 1,
            ContainerLength.forty_feet: 0,
            ContainerLength.forty_five_feet: 0,
            ContainerLength.other: 0
        })
        ContainerFlowGenerationProperties.create(
            start_date=now,
            end_date=now + datetime.timedelta(weeks=2)
        )  # mostly use default values
        arrival_distribution = {0: 0.0,
                                1: 0.0,
                                2: 0.0,
                                3: 0.0,
                                4: 0.0,
                                5: 0.0039591265543534575,
                                6: 0.008280755354708402,
                                7: 0.00787052138708076,
                                8: 0.009048448164603814,
                                9: 0.010653252222483504,
                                10: 0.012752141622641803,
                                11: 0.016642037255734387,
                                12: 0.014028517880762,
                                13: 0.014804115031537253,
                                14: 0.014974413128949352,
                                15: 0.011139325718994135,
                                16: 0.013892795598075644,
                                17: 0.01082340227148447,
                                18: 0.008328057746798652,
                                19: 0.006987426702627708,
                                20: 0.005148702946956847,
                                21: 0.0030022110241690898,
                                22: 0.0022556664886468924,
                                23: 0.002490824815783658,
                                24: 0.001903829363512033,
                                25: 0.0021963463393818504,
                                26: 0.001702371138626582,
                                27: 0.0021438383478597847,
                                28: 0.0024202228363111615,
                                29: 0.006458109051981418,
                                30: 0.009296920847765565,
                                31: 0.008129901930327036,
                                32: 0.009348584294496615,
                                33: 0.011340930095712323,
                                34: 0.013698448606867216,
                                35: 0.01296799663104594,
                                36: 0.015331193639106963,
                                37: 0.014188986240397503,
                                38: 0.014878231656167027,
                                39: 0.01218616653188358,
                                40: 0.012107579394020204,
                                41: 0.010917000115475164,
                                42: 0.006806732487834122,
                                43: 0.005802918750649381,
                                44: 0.005287802279192979,
                                45: 0.0028202830127811215,
                                46: 0.0019358005313836828,
                                47: 0.0024196460473237236,
                                48: 0.0016307576755443523,
                                49: 0.0019988666796929904,
                                50: 0.001446034417884346,
                                51: 0.0010097489273788896,
                                52: 0.0022229861377374384,
                                53: 0.008228976109664983,
                                54: 0.00916729394725238,
                                55: 0.008981193048564363,
                                56: 0.010437595120044508,
                                57: 0.011883447250428468,
                                58: 0.013126241314098189,
                                59: 0.0140232137102564,
                                60: 0.014067510063763042,
                                61: 0.017925057408950704,
                                62: 0.014893617277832918,
                                63: 0.01301145426124103,
                                64: 0.012079362990869175,
                                65: 0.010112961782918234,
                                66: 0.00893673181616467,
                                67: 0.006631710275002562,
                                68: 0.004326674554006004,
                                69: 0.004305598082248182,
                                70: 0.0022903162137174965,
                                71: 0.0024661555911701296,
                                72: 0.0011415664927662006,
                                73: 0.0012494109397148158,
                                74: 0.0009989509275061823,
                                75: 0.0009419532259761962,
                                76: 0.002040252335905318,
                                77: 0.00518431625514197,
                                78: 0.009913000508486947,
                                79: 0.010654141394182583,
                                80: 0.010344655620812727,
                                81: 0.012472178423578372,
                                82: 0.015253769000857457,
                                83: 0.015313545656682602,
                                84: 0.01971921057376204,
                                85: 0.016488565599922105,
                                86: 0.016894274684674377,
                                87: 0.015499123208186931,
                                88: 0.01478237177250456,
                                89: 0.012150479118805851,
                                90: 0.008135216144988145,
                                91: 0.006333340451456769,
                                92: 0.006095849295750999,
                                93: 0.004708883365054937,
                                94: 0.003413326087863949,
                                95: 0.0017118289895981984,
                                96: 0.0026912758548089605,
                                97: 0.0021584624941145677,
                                98: 0.0023228922170533146,
                                99: 0.001604168692757123,
                                100: 0.0027305554397402476,
                                101: 0.0065523938632102915,
                                102: 0.009520380832912196,
                                103: 0.010997001773196237,
                                104: 0.010602136875550094,
                                105: 0.015899660970804596,
                                106: 0.018083220148664984,
                                107: 0.0163816471763427,
                                108: 0.01629007302430533,
                                109: 0.019168920074881534,
                                110: 0.01646589595887871,
                                111: 0.013656904790633789,
                                112: 0.012617169136636602,
                                113: 0.009685606800402495,
                                114: 0.009069337128450136,
                                115: 0.004422493262915178,
                                116: 0.0042658850465993456,
                                117: 0.0030436628208826318,
                                118: 0.0016924428501923685,
                                119: 0.002152265219068244,
                                120: 0.0028091995053135693,
                                121: 0.0022128380816916287,
                                122: 0.0020158483718963533,
                                123: 0.0010395871009478725,
                                124: 0.0009474696390102265,
                                125: 0.0011628071003245448,
                                126: 0.001418797422137764,
                                127: 0.0016522620284370162,
                                128: 0.0015376248047583672,
                                129: 0.0014253278743416424,
                                130: 0.0007202777097896012,
                                131: 0.0005074102872076632,
                                132: 0.0004608008040356385,
                                133: 0.0,
                                134: 0.0,
                                135: 0.0,
                                136: 0.0,
                                137: 0.0,
                                138: 0.0,
                                139: 0.0,
                                140: 0.0,
                                141: 0.0,
                                142: 0.0,
                                143: 0.0,
                                144: 0.0,
                                145: 0.0,
                                146: 0.0,
                                147: 0.0,
                                148: 0.0,
                                149: 0.0,
                                150: 0.0,
                                151: 0.0,
                                152: 0.0,
                                153: 0.0,
                                154: 0.0,
                                155: 0.0,
                                156: 0.0,
                                157: 0.0,
                                158: 0.0,
                                159: 0.0,
                                160: 0.0,
                                161: 0.0,
                                162: 0.0,
                                163: 0.0,
                                164: 0.0,
                                165: 0.0,
                                166: 0.0,
                                167: 0.0}
        truck_arrival_distribution_manager = TruckArrivalDistributionManager()
        truck_arrival_distribution_manager.set_truck_arrival_distribution(arrival_distribution)

        self.preview_report = TruckGateThroughputPreviewReport()

    def test_report_without_schedule(self):
        report = self.preview_report.get_report_as_graph()
        self.assertIsNotNone(report)

    def test_report_with_schedule(self):
        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_every_k_days=-1,
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=24000,
            average_moved_capacity=24000
        )
        report = self.preview_report.get_report_as_graph()
        self.assertIsNotNone(report)

    def test_text_report(self):
        # pylint: disable=protected-access
        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_every_k_days=-1,
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=24000,
            average_moved_capacity=24000
        )
        report = self.preview_report.get_report_as_text()
        # flake8: noqa: W291 (ignore trailing whitespace in text report)
        expected_report = \
            '''Hourly view:
                 Minimum (trucks/h)  Maximum (trucks/h)  Average (trucks/h)  Sum (trucks/24h)
Day of the week                                                                              
Monday                            0                  80                  36               854
Tuesday                           8                  74                  37               894
Wednesday                         4                  86                  39               936
Thursday                          4                  94                  42              1016
Friday                            8                  92                  42              1016
Saturday                          0                  14                   4                84
Sunday                            0                   0                   0                 0
Total                             0                  94                  29              4800
Fewest trucks in a day: 0 on Sunday
Most trucks in a day: 1016 on Thursday
Average trucks per day: 685'''
        self.assertEqual(report, expected_report)
        updated_preview = self.preview_report._get_updated_preview()
        self.assertIsNotNone(updated_preview)
