import unittest

from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.truck_arrival_distribution_repository import \
    TruckArrivalDistributionRepository
from conflowgen.domain_models.distribution_seeders import truck_arrival_distribution_seeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckArrivalDistributionRepository(unittest.TestCase):
    default_data = {
        0: 0.006944444444444444,
        1: 0.006944444444444444,
        2: 0.006944444444444444,
        3: 0.006944444444444444,
        4: 0.006944444444444444,
        5: 0.006944444444444444,
        6: 0.006944444444444444,
        7: 0.006944444444444444,
        8: 0.006944444444444444,
        9: 0.006944444444444444,
        10: 0.006944444444444444,
        11: 0.006944444444444444,
        12: 0.006944444444444444,
        13: 0.006944444444444444,
        14: 0.006944444444444444,
        15: 0.006944444444444444,
        16: 0.006944444444444444,
        17: 0.006944444444444444,
        18: 0.006944444444444444,
        19: 0.006944444444444444,
        20: 0.006944444444444444,
        21: 0.006944444444444444,
        22: 0.006944444444444444,
        23: 0.006944444444444444,
        24: 0.006944444444444444,
        25: 0.006944444444444444,
        26: 0.006944444444444444,
        27: 0.006944444444444444,
        28: 0.006944444444444444,
        29: 0.006944444444444444,
        30: 0.006944444444444444,
        31: 0.006944444444444444,
        32: 0.006944444444444444,
        33: 0.006944444444444444,
        34: 0.006944444444444444,
        35: 0.006944444444444444,
        36: 0.006944444444444444,
        37: 0.006944444444444444,
        38: 0.006944444444444444,
        39: 0.006944444444444444,
        40: 0.006944444444444444,
        41: 0.006944444444444444,
        42: 0.006944444444444444,
        43: 0.006944444444444444,
        44: 0.006944444444444444,
        45: 0.006944444444444444,
        46: 0.006944444444444444,
        47: 0.006944444444444444,
        48: 0.006944444444444444,
        49: 0.006944444444444444,
        50: 0.006944444444444444,
        51: 0.006944444444444444,
        52: 0.006944444444444444,
        53: 0.006944444444444444,
        54: 0.006944444444444444,
        55: 0.006944444444444444,
        56: 0.006944444444444444,
        57: 0.006944444444444444,
        58: 0.006944444444444444,
        59: 0.006944444444444444,
        60: 0.006944444444444444,
        61: 0.006944444444444444,
        62: 0.006944444444444444,
        63: 0.006944444444444444,
        64: 0.006944444444444444,
        65: 0.006944444444444444,
        66: 0.006944444444444444,
        67: 0.006944444444444444,
        68: 0.006944444444444444,
        69: 0.006944444444444444,
        70: 0.006944444444444444,
        71: 0.006944444444444444,
        72: 0.006944444444444444,
        73: 0.006944444444444444,
        74: 0.006944444444444444,
        75: 0.006944444444444444,
        76: 0.006944444444444444,
        77: 0.006944444444444444,
        78: 0.006944444444444444,
        79: 0.006944444444444444,
        80: 0.006944444444444444,
        81: 0.006944444444444444,
        82: 0.006944444444444444,
        83: 0.006944444444444444,
        84: 0.006944444444444444,
        85: 0.006944444444444444,
        86: 0.006944444444444444,
        87: 0.006944444444444444,
        88: 0.006944444444444444,
        89: 0.006944444444444444,
        90: 0.006944444444444444,
        91: 0.006944444444444444,
        92: 0.006944444444444444,
        93: 0.006944444444444444,
        94: 0.006944444444444444,
        95: 0.006944444444444444,
        96: 0.006944444444444444,
        97: 0.006944444444444444,
        98: 0.006944444444444444,
        99: 0.006944444444444444,
        100: 0.006944444444444444,
        101: 0.006944444444444444,
        102: 0.006944444444444444,
        103: 0.006944444444444444,
        104: 0.006944444444444444,
        105: 0.006944444444444444,
        106: 0.006944444444444444,
        107: 0.006944444444444444,
        108: 0.006944444444444444,
        109: 0.006944444444444444,
        110: 0.006944444444444444,
        111: 0.006944444444444444,
        112: 0.006944444444444444,
        113: 0.006944444444444444,
        114: 0.006944444444444444,
        115: 0.006944444444444444,
        116: 0.006944444444444444,
        117: 0.006944444444444444,
        118: 0.006944444444444444,
        119: 0.006944444444444444,
        120: 0.006944444444444444,
        121: 0.006944444444444444,
        122: 0.006944444444444444,
        123: 0.006944444444444444,
        124: 0.006944444444444444,
        125: 0.006944444444444444,
        126: 0.006944444444444444,
        127: 0.006944444444444444,
        128: 0.006944444444444444,
        129: 0.006944444444444444,
        130: 0.006944444444444444,
        131: 0.006944444444444444,
        132: 0.006944444444444444,
        133: 0.006944444444444444,
        134: 0.006944444444444444,
        135: 0.006944444444444444,
        136: 0.006944444444444444,
        137: 0.006944444444444444,
        138: 0.006944444444444444,
        139: 0.006944444444444444,
        140: 0.006944444444444444,
        141: 0.006944444444444444,
        142: 0.006944444444444444,
        143: 0.006944444444444444,
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

    half_hourly_data = {
        0.0: 0.0,
        0.5: 0.0,
        1.0: 0.0,
        1.5: 0.0,
        2.0: 0.0,
        2.5: 0.0,
        3.0: 0.0,
        3.5: 0.0,
        4.0: 0.0,
        4.5: 0.0,
        5.0: 0.0,
        5.5: 0.0,
        6.0: 0.0,
        6.5: 0.0,
        7.0: 0.0,
        7.5: 0.0,
        8.0: 0.005847356259863457,
        8.5: 0.005847356259863457,
        9.0: 0.006884424813828916,
        9.5: 0.006884424813828916,
        10.0: 0.008240784915529742,
        10.5: 0.008240784915529742,
        11.0: 0.010754542541876863,
        11.5: 0.010754542541876863,
        12.0: 0.009065614385411223,
        12.5: 0.009065614385411223,
        13.0: 0.00956682661232754,
        13.5: 0.00956682661232754,
        14.0: 0.009676877930280697,
        14.5: 0.009676877930280697,
        15.0: 0.007198538886305298,
        15.5: 0.007198538886305298,
        16.0: 0.008977906910623057,
        16.5: 0.008977906910623057,
        17.0: 0.0069943804588238085,
        17.5: 0.0069943804588238085,
        18.0: 0.005381820143341635,
        18.5: 0.005381820143341635,
        19.0: 0.004515467462119917,
        19.5: 0.004515467462119917,
        20.0: 0.003327233560870352,
        20.5: 0.0,
        21.0: 0.0,
        21.5: 0.0,
        22.0: 0.0,
        22.5: 0.0,
        23.0: 0.0,
        23.5: 0.0,
        24.0: 0.0,
        24.5: 0.0,
        25.0: 0.0,
        25.5: 0.0,
        26.0: 0.0,
        26.5: 0.0,
        27.0: 0.0,
        27.5: 0.0,
        28.0: 0.0,
        28.5: 0.0,
        29.0: 0.0,
        29.5: 0.0,
        30.0: 0.0,
        30.5: 0.0,
        31.0: 0.0,
        31.5: 0.0,
        32.0: 0.006041312488159616,
        32.5: 0.006041312488159616,
        33.0: 0.007328821183642256,
        33.5: 0.007328821183642256,
        34.0: 0.008852314535559925,
        34.5: 0.008852314535559925,
        35.0: 0.00838027636330664,
        35.5: 0.00838027636330664,
        36.0: 0.009907439316224021,
        36.5: 0.009907439316224021,
        37.0: 0.009169313456252479,
        37.5: 0.009169313456252479,
        38.0: 0.009614722815201775,
        38.5: 0.009614722815201775,
        39.0: 0.00787503623358249,
        39.5: 0.00787503623358249,
        40.0: 0.007824251062007128,
        40.5: 0.007824251062007128,
        41.0: 0.00705486596186395,
        41.5: 0.00705486596186395,
        42.0: 0.004398697886964745,
        42.5: 0.004398697886964745,
        43.0: 0.003750005820315642,
        43.5: 0.003750005820315642,
        44.0: 0.0034171233780298876,
        44.5: 0.0,
        45.0: 0.0,
        45.5: 0.0,
        46.0: 0.0,
        46.5: 0.0,
        47.0: 0.0,
        47.5: 0.0,
        48.0: 0.0,
        48.5: 0.0,
        49.0: 0.0,
        49.5: 0.0,
        50.0: 0.0,
        50.5: 0.0,
        51.0: 0.0,
        51.5: 0.0,
        52.0: 0.0,
        52.5: 0.0,
        53.0: 0.0,
        53.5: 0.0,
        54.0: 0.0,
        54.5: 0.0,
        55.0: 0.0,
        55.5: 0.0,
        56.0: 0.006745061258333995,
        56.5: 0.006745061258333995,
        57.0: 0.007679410701646271,
        57.5: 0.007679410701646271,
        58.0: 0.008482538433133749,
        58.5: 0.008482538433133749,
        59.0: 0.009062186684434759,
        59.5: 0.009062186684434759,
        60.0: 0.00909081220731496,
        60.5: 0.00909081220731496,
        61.0: 0.011583665479640732,
        61.5: 0.011583665479640732,
        62.0: 0.009624665427407022,
        62.5: 0.009624665427407022,
        63.0: 0.008408359880097303,
        63.5: 0.008408359880097303,
        64.0: 0.007806016845642667,
        64.5: 0.007806016845642667,
        65.0: 0.006535274260445081,
        65.5: 0.006535274260445081,
        66.0: 0.0057751620805421774,
        66.5: 0.0057751620805421774,
        67.0: 0.004285593715597633,
        67.5: 0.004285593715597633,
        68.0: 0.002796016187253771,
        68.5: 0.0,
        69.0: 0.0,
        69.5: 0.0,
        70.0: 0.0,
        70.5: 0.0,
        71.0: 0.0,
        71.5: 0.0,
        72.0: 0.0,
        72.5: 0.0,
        73.0: 0.0,
        73.5: 0.0,
        74.0: 0.0,
        74.5: 0.0,
        75.0: 0.0,
        75.5: 0.0,
        76.0: 0.0,
        76.5: 0.0,
        77.0: 0.0,
        77.5: 0.0,
        78.0: 0.0,
        78.5: 0.0,
        79.0: 0.0,
        79.5: 0.0,
        80.0: 0.00668500119579781,
        80.5: 0.00668500119579781,
        81.0: 0.008059864990389558,
        81.5: 0.008059864990389558,
        82.0: 0.009857405383896607,
        82.5: 0.009857405383896607,
        83.0: 0.00989603470422583,
        83.5: 0.00989603470422583,
        84.0: 0.012743096638284358,
        84.5: 0.012743096638284358,
        85.0: 0.010655364933628404,
        85.5: 0.010655364933628404,
        86.0: 0.010917545311219544,
        86.5: 0.010917545311219544,
        87.0: 0.010015960025975905,
        87.5: 0.010015960025975905,
        88.0: 0.00955277551986375,
        88.5: 0.00955277551986375,
        89.0: 0.007851974044966025,
        89.5: 0.007851974044966025,
        90.0: 0.005257200592342844,
        90.5: 0.005257200592342844,
        91.0: 0.004092778923079977,
        91.5: 0.004092778923079977,
        92.0: 0.003939305601388119,
        92.5: 0.0,
        93.0: 0.0,
        93.5: 0.0,
        94.0: 0.0,
        94.5: 0.0,
        95.0: 0.0,
        95.5: 0.0,
        96.0: 0.0,
        96.5: 0.0,
        97.0: 0.0,
        97.5: 0.0,
        98.0: 0.0,
        98.5: 0.0,
        99.0: 0.0,
        99.5: 0.0,
        100.0: 0.0,
        100.5: 0.0,
        101.0: 0.0,
        101.5: 0.0,
        102.0: 0.0,
        102.5: 0.0,
        103.0: 0.0,
        103.5: 0.0,
        104.0: 0.006851392669705531,
        104.5: 0.006851392669705531,
        105.0: 0.010274798552864527,
        105.5: 0.010274798552864527,
        106.0: 0.011685874595427376,
        106.5: 0.011685874595427376,
        107.0: 0.01058627130541297,
        107.5: 0.01058627130541297,
        108.0: 0.010527093567814597,
        108.5: 0.010527093567814597,
        109.0: 0.012387483771322302,
        109.5: 0.012387483771322302,
        110.0: 0.010640715187610906,
        110.5: 0.010640715187610906,
        111.0: 0.00882546777802846,
        111.5: 0.00882546777802846,
        112.0: 0.008153561979994874,
        112.5: 0.008153561979994874,
        113.0: 0.006259105707922169,
        113.5: 0.006259105707922169,
        114.0: 0.005860855283263588,
        114.5: 0.005860855283263588,
        115.0: 0.0028579368743328936,
        115.5: 0.0028579368743328936,
        116.0: 0.002756732334354128,
        116.5: 0.0,
        117.0: 0.0,
        117.5: 0.0,
        118.0: 0.0,
        118.5: 0.0,
        119.0: 0.0,
        119.5: 0.0,
        120.0: 0.0,
        120.5: 0.0,
        121.0: 0.0,
        121.5: 0.0,
        122.0: 0.0,
        122.5: 0.0,
        123.0: 0.0,
        123.5: 0.0,
        124.0: 0.0,
        124.5: 0.0,
        125.0: 0.0,
        125.5: 0.0,
        126.0: 0.0,
        126.5: 0.0,
        127.0: 0.0,
        127.5: 0.0,
        128.0: 0.0009936554715091123,
        128.5: 0.0009936554715091123,
        129.0: 0.0009210861041335698,
        129.5: 0.0009210861041335698,
        130.0: 0.0004654632814999111,
        130.5: 0.0004654632814999111,
        131.0: 0.0003279024939137455,
        131.5: 0.0003279024939137455,
        132.0: 0.00029778216297555397,
        132.5: 0.00029778216297555397,
        133.0: 0.0,
        133.5: 0.0,
        134.0: 0.0,
        134.5: 0.0,
        135.0: 0.0,
        135.5: 0.0,
        136.0: 0.0,
        136.5: 0.0,
        137.0: 0.0,
        137.5: 0.0,
        138.0: 0.0,
        138.5: 0.0,
        139.0: 0.0,
        139.5: 0.0,
        140.0: 0.0,
        140.5: 0.0,
        141.0: 0.0,
        141.5: 0.0,
        142.0: 0.0,
        142.5: 0.0,
        143.0: 0.0,
        143.5: 0.0,
        144.0: 0.0,
        144.5: 0.0,
        145.0: 0.0,
        145.5: 0.0,
        146.0: 0.0,
        146.5: 0.0,
        147.0: 0.0,
        147.5: 0.0,
        148.0: 0.0,
        148.5: 0.0,
        149.0: 0.0,
        149.5: 0.0,
        150.0: 0.0,
        150.5: 0.0,
        151.0: 0.0,
        151.5: 0.0,
        152.0: 0.0,
        152.5: 0.0,
        153.0: 0.0,
        153.5: 0.0,
        154.0: 0.0,
        154.5: 0.0,
        155.0: 0.0,
        155.5: 0.0,
        156.0: 0.0,
        156.5: 0.0,
        157.0: 0.0,
        157.5: 0.0,
        158.0: 0.0,
        158.5: 0.0,
        159.0: 0.0,
        159.5: 0.0,
        160.0: 0.0,
        160.5: 0.0,
        161.0: 0.0,
        161.5: 0.0,
        162.0: 0.0,
        162.5: 0.0,
        163.0: 0.0,
        163.5: 0.0,
        164.0: 0.0,
        164.5: 0.0,
        165.0: 0.0,
        165.5: 0.0,
        166.0: 0.0,
        166.5: 0.0,
        167.0: 0.0,
        167.5: 0.0
    }

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            TruckArrivalDistribution
        ])
        truck_arrival_distribution_seeder.seed()
        self.repository = TruckArrivalDistributionRepository()

    def test_get(self):
        distribution = self.repository.get_distribution()
        self.assertTrue(type(distribution), dict)
        hour_in_the_week_values = distribution.keys()
        self.assertGreaterEqual(min(hour_in_the_week_values), 0)
        self.assertLessEqual(max(hour_in_the_week_values), (24 * 7))
        sum_of_all_fractions = sum(distribution.values())
        self.assertAlmostEqual(sum_of_all_fractions, 1)

    def test_happy_path(self):
        self.repository.set_distribution(
            self.default_data
        )
        self.assertDictEqual(
            self.default_data,
            self.repository.get_distribution()
        )

    def test_happy_path_with_half_hourly_data(self):
        self.repository.set_distribution(
            self.half_hourly_data
        )
        self.assertDictEqual(
            self.half_hourly_data,
            self.repository.get_distribution()
        )

    def test_set_twice(self):
        """e.g., no exception is thrown while refreshing the data in the database.
        """
        self.repository.set_distribution(
            self.default_data
        )
        self.repository.set_distribution(
            self.default_data
        )
        self.assertDictEqual(
            self.default_data,
            self.repository.get_distribution()
        )
