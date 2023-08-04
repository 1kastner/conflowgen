import unittest
import datetime
from functools import wraps

from conflowgen import ContainerLength, TruckArrivalDistributionManager, ModeOfTransport, TruckGateThroughputPreview
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.data_summaries.data_summaries_cache import DataSummariesCache
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestDataSummariesCache(unittest.TestCase):

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
        self.now = datetime.datetime.now()
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
            start_date=self.now,
            end_date=self.now + datetime.timedelta(weeks=2)
        )  # mostly use default values
        arrival_distribution = {
            3: .2,
            4: .8
        }
        truck_arrival_distribution_manager = TruckArrivalDistributionManager()
        truck_arrival_distribution_manager.set_truck_arrival_distribution(arrival_distribution)
        self.preview = TruckGateThroughputPreview(
            start_date=self.now.date(),
            end_date=(self.now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.0
        )
        self.cache = DataSummariesCache()  # This is technically incorrect usage of the cache as it should never be
        # instantiated, but it's the easiest way to test it

    def test_sanity(self):
        # Define a function to be decorated
        @DataSummariesCache.cache_result
        # pylint: disable=invalid-name
        def my_function(n):
            return n ** 2

        # Test case 1: Call the decorated function with argument 5
        result = my_function(5)
        self.assertEqual(result, 25, "Result of 5^2 should be 25")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "There should be one cached result")
        self.assertEqual(list(DataSummariesCache.cached_results.values())[0], 25, "Cached result should be 25")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'my_function': 1}, "Hit counter should be 1")

        # Test case 2: Call the decorated function with argument 5 again
        # This should retrieve the cached result from the previous call
        result = my_function(5)
        self.assertEqual(result, 25, "Result of 5^2 should be 25")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "There should be one cached result")
        self.assertEqual(list(DataSummariesCache.cached_results.values())[0], 25, "Cached result should be 25")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'my_function': 2}, "Hit counter should be 2")

        # Test case 3: Call the decorated function with argument 10
        result = my_function(10)
        self.assertEqual(result, 100, "Result of 10^2 should be 100")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "There should be two cached results")
        self.assertTrue(25 in list(DataSummariesCache.cached_results.values()) and
                        100 in list(DataSummariesCache.cached_results.values()), "Cached results should be 25 and 100")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'my_function': 3}, "Hit counter should be 3")

    def test_with_preview(self):
        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_every_k_days=-1,
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300
        )
        preview = self.preview.get_weekly_truck_arrivals(True, True)
        self.assertEqual(preview, {3: 12, 4: 48}, "Uncached result is incorrect")
        self.assertEqual(len(DataSummariesCache.cached_results), 9, "There should be 9 cached results")
        self.assertTrue(59.999999999999986 in list(DataSummariesCache.cached_results.values()) and
                        {3: 12, 4: 48} in list(DataSummariesCache.cached_results.values()), "Incorrect results cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'_get_number_of_trucks_per_week': 1,
                                                           '_get_total_trucks': 1,
                                                           'get_truck_capacity_for_export_containers': 2,
                                                           'get_inbound_capacity_of_vehicles': 3,
                                                           'get_outbound_capacity_of_vehicles': 2,
                                                           'get_weekly_truck_arrivals': 1}, "Incorrect hit counter")

        preview = self.preview.get_weekly_truck_arrivals(True, True)
        self.assertEqual(preview, {3: 12, 4: 48}, "Uncached result is incorrect")
        self.assertEqual(len(DataSummariesCache.cached_results), 9, "There should be 9 cached results")
        self.assertTrue(59.999999999999986 in list(DataSummariesCache.cached_results.values()) and
                        {3: 12, 4: 48} in list(DataSummariesCache.cached_results.values()), "Incorrect results cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'_get_number_of_trucks_per_week': 1,
                                                           '_get_total_trucks': 1,
                                                           'get_truck_capacity_for_export_containers': 2,
                                                           'get_inbound_capacity_of_vehicles': 3,
                                                           'get_outbound_capacity_of_vehicles': 2,
                                                           'get_weekly_truck_arrivals': 2}, "Incorrect hit counter")
        # Only get_weekly_truck_arrivals should be called again as the other functions are cached

    def test_with_adjusted_preview(self):
        # Create a preview, adjust input distribution, then create another preview
        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_every_k_days=-1,
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300
        )
        preview = self.preview.get_weekly_truck_arrivals(True, True)
        self.assertEqual(preview, {3: 12, 4: 48}, "Uncached result is incorrect")
        self.assertEqual(len(DataSummariesCache.cached_results), 9, "There should be 9 cached results")
        self.assertTrue(59.999999999999986 in list(DataSummariesCache.cached_results.values()) and
                        {3: 12, 4: 48} in list(DataSummariesCache.cached_results.values()), "Incorrect results cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'_get_number_of_trucks_per_week': 1,
                                                           '_get_total_trucks': 1,
                                                           'get_truck_capacity_for_export_containers': 2,
                                                           'get_inbound_capacity_of_vehicles': 3,
                                                           'get_outbound_capacity_of_vehicles': 2,
                                                           'get_weekly_truck_arrivals': 1}, "Incorrect hit counter")

        arrival_distribution = {
            3: .1,
            4: .4,
            5: .5
        }
        truck_arrival_distribution_manager = TruckArrivalDistributionManager()
        truck_arrival_distribution_manager.set_truck_arrival_distribution(arrival_distribution)
        self.preview = TruckGateThroughputPreview(
            start_date=self.now.date(),
            end_date=(self.now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.0
        )
        preview = self.preview.get_weekly_truck_arrivals(True, True)
        self.assertEqual(preview, {3: 6, 4: 24, 5: 30}, "New result is incorrect")
        self.assertEqual(len(DataSummariesCache.cached_results), 9, "There should be 9 cached results, because"
                                                                    "the preview was adjusted")
        self.assertTrue(59.999999999999986 in list(DataSummariesCache.cached_results.values()) and
                        {3: 6, 4: 24, 5: 30} in list(DataSummariesCache.cached_results.values()),
                        "Incorrect results cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'_get_number_of_trucks_per_week': 1,
                                                           '_get_total_trucks': 1,
                                                           'get_truck_capacity_for_export_containers': 2,
                                                           'get_inbound_capacity_of_vehicles': 3,
                                                           'get_outbound_capacity_of_vehicles': 2,
                                                           'get_weekly_truck_arrivals': 1}, "Incorrect hit counter")
        # Hit counter should be the same as before, because the preview was adjusted i.e. the cache was reset, and then
        # we re-ran the same functions

    def test_cache_reset(self):
        @DataSummariesCache.cache_result
        def increment_counter(counter):
            return counter + 1

        # Check initial state
        self.assertEqual(len(DataSummariesCache.cached_results), 0, "Initial cache should be empty")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {}, "Initial hit counter should be empty")

        # Call the function and check cache and hit counter
        result = increment_counter(5)
        self.assertEqual(result, 6, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue(6 in list(DataSummariesCache.cached_results.values()), "Incorrect results cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'increment_counter': 1},
                         "Hit counter should be 1 for 'increment_counter'")

        # Reset cache and check again
        DataSummariesCache.reset_cache()
        self.assertEqual(len(DataSummariesCache.cached_results), 0, "Cache should be empty after reset")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {}, "Hit counter should be empty after reset")

    def test_cache_with_different_function_args(self):
        @DataSummariesCache.cache_result
        # pylint: disable=invalid-name
        def add_numbers(a, b):
            return a + b

        # Call the function with different arguments and check if the results are cached correctly
        result1 = add_numbers(1, 2)
        result2 = add_numbers(3, 4)
        self.assertEqual(result1, 3, "Incorrect result returned")
        self.assertEqual(result2, 7, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "Cache should have two results")
        self.assertTrue(3 in list(DataSummariesCache.cached_results.values()) and
                        7 in list(DataSummariesCache.cached_results.values()), "Cached results should be 3 and 7")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'add_numbers': 2},
                         "Hit counter should be 2 for 'add_numbers'")

        # Call the function with the same arguments and check if the results are retrieved from the cache
        result3 = add_numbers(1, 2)
        self.assertEqual(result3, 3, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "Cache should still have two results")
        self.assertTrue(3 in list(DataSummariesCache.cached_results.values()) and
                        7 in list(DataSummariesCache.cached_results.values()), "Cached results should be 3 and 7")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'add_numbers': 3},
                         "Hit counter should be 3 for 'add_numbers'")

    def test_cache_with_different_functions(self):
        @DataSummariesCache.cache_result
        # pylint: disable=invalid-name
        def square(n):
            return n ** 2

        @DataSummariesCache.cache_result
        # pylint: disable=invalid-name
        def cube(n):
            return n ** 3

        # Call the functions and check if the results are cached correctly
        result1 = square(5)
        result2 = cube(5)
        self.assertEqual(result1, 25, "Incorrect result returned")
        self.assertEqual(result2, 125, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "Cache should have two results")
        self.assertTrue(25 in list(DataSummariesCache.cached_results.values()) and
                        125 in list(DataSummariesCache.cached_results.values()), "Cached results should be 25 and 125")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'square': 1, 'cube': 1},
                         "Hit counter should be 1 for both 'square' and 'cube'")

        # Call the functions again and check if the results are retrieved from the cache
        result3 = square(5)
        result4 = cube(5)
        self.assertEqual(result3, 25, "Incorrect result returned")
        self.assertEqual(result4, 125, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "Cache should still have two results")
        self.assertTrue(25 in list(DataSummariesCache.cached_results.values()) and
                        125 in list(DataSummariesCache.cached_results.values()), "Cached results should be 25 and 125")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'square': 2, 'cube': 2},
                         "Hit counter should be 2 for both 'square' and 'cube'")

    def test_cache_with_no_args(self):
        @DataSummariesCache.cache_result
        def get_constant():
            return 42

        # Call the function and check if the result is cached
        constant1 = get_constant()
        self.assertEqual(constant1, 42, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue(42 in list(DataSummariesCache.cached_results.values()), "Cached result should be 42")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'get_constant': 1},
                         "Hit counter should be 1 for 'get_constant'")

        # Call the function again and check if the result is retrieved from the cache
        constant2 = get_constant()
        self.assertEqual(constant2, 42, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should still have one result")
        self.assertTrue(42 in list(DataSummariesCache.cached_results.values()), "Cached result should still be 42")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'get_constant': 2},
                         "Hit counter should be 2 for 'get_constant'")

    def test_cache_with_default_args(self):
        @DataSummariesCache.cache_result
        # pylint: disable=invalid-name
        def power(n, p=2):
            return n ** p

        # Call the function with and without default argument and check if the results are cached correctly
        result1 = power(5)
        result2 = power(5, 3)
        self.assertEqual(result1, 25, "Incorrect result returned")
        self.assertEqual(result2, 125, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "Cache should have two results")
        self.assertTrue(25 in list(DataSummariesCache.cached_results.values()) and
                        125 in list(DataSummariesCache.cached_results.values()), "Cached results should be 25 and 125")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'power': 2}, "Hit counter should be 2 for 'power'")

        # Call the function with the same arguments and check if the results are retrieved from the cache
        result3 = power(5)
        result4 = power(5, 3)
        self.assertEqual(result3, 25, "Incorrect result returned")
        self.assertEqual(result4, 125, "Incorrect result returned")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "Cache should still have two results")
        self.assertTrue(25 in list(DataSummariesCache.cached_results.values()) and
                        125 in list(DataSummariesCache.cached_results.values()), "Cached results should be 25 and 125")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'power': 4}, "Hit counter should be 4 for 'power'")

    def test_docstring_preservation(self):
        @DataSummariesCache.cache_result
        # pylint: disable=invalid-name
        def square(n):
            """Return the square of a number."""
            return n ** 2

        self.assertEqual(square.__doc__, "Return the square of a number.", "Docstring should be preserved")

        @DataSummariesCache.cache_result
        # pylint: disable=invalid-name
        def cube(n):
            """Return the cube of a number."""
            return n ** 3

        self.assertEqual(cube.__doc__, "Return the cube of a number.", "Docstring should be preserved")

    def test_cache_none(self):
        @DataSummariesCache.cache_result
        def return_none():
            return None

        self.assertEqual(return_none(), None, "Function should return None")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue(None in list(DataSummariesCache.cached_results.values()), "None should be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'return_none': 1})

    def test_cache_float(self):
        @DataSummariesCache.cache_result
        def return_float():
            return 3.14

        self.assertEqual(return_float(), 3.14, "Function should return float")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue(3.14 in list(DataSummariesCache.cached_results.values()), "Float should be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'return_float': 1})

    def test_cache_string(self):
        @DataSummariesCache.cache_result
        def return_string():
            return "hello"

        self.assertEqual(return_string(), "hello", "Function should return string")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue("hello" in list(DataSummariesCache.cached_results.values()), "String should be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'return_string': 1})

    def test_cache_list(self):
        @DataSummariesCache.cache_result
        def return_list():
            return [1, 2, 3]

        self.assertEqual(return_list(), [1, 2, 3], "Function should return list")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue([1, 2, 3] in list(DataSummariesCache.cached_results.values()), "List should be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'return_list': 1})

    def test_cache_dictionary(self):
        @DataSummariesCache.cache_result
        def return_dictionary():
            return {"a": 1, "b": 2}

        self.assertEqual(return_dictionary(), {"a": 1, "b": 2}, "Function should return dictionary")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue({"a": 1, "b": 2} in list(DataSummariesCache.cached_results.values()), "Dictionary should be "
                                                                                              "cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'return_dictionary': 1})

    def test_cache_custom_object(self):
        class CustomObject:
            pass

        @DataSummariesCache.cache_result
        def return_custom_object():
            return CustomObject()

        self.assertIsInstance(return_custom_object(), CustomObject, "Function should return custom object")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertIsInstance(list(DataSummariesCache.cached_results.values())[0], CustomObject,
                              "Function should return an instance of CustomObject")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'return_custom_object': 1})

    def test_nested_decorator(self):
        # pylint: disable=invalid-name
        def simple_decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                return f(*args, **kwargs)

            return wrapper

        @DataSummariesCache.cache_result
        @simple_decorator
        # pylint: disable=invalid-name
        def add(a, b):
            """Adds two numbers."""
            return a + b

        # Initial call
        result = add(1, 2)
        self.assertEqual(result, 3, "Function should return the sum of the two arguments")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue(3 in list(DataSummariesCache.cached_results.values()), "Result should be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'add': 1}, "Cache should have one hit")

        # Repeated call
        result = add(1, 2)
        self.assertEqual(result, 3, "Function should return the sum of the two arguments (from cache)")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should still have one result")
        self.assertTrue(3 in list(DataSummariesCache.cached_results.values()), "Result should still be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter, {'add': 2}, "Cache should have two hits")

        # Check function metadata
        self.assertEqual(add.__name__, 'add', "Function name should be preserved")
        self.assertEqual(add.__doc__.strip(), 'Adds two numbers.', "Docstring should be preserved")

    def test_class_methods(self):
        class TestClass:
            def __init__(self):
                self.counter = 0

            @DataSummariesCache.cache_result
            # pylint: disable=invalid-name
            def method(self, a, b):
                """Adds two numbers and the instance counter."""
                self.counter = getattr(self, 'counter', 0) + 1
                return a + b + self.counter

        # Create instance and call method
        instance = TestClass()
        result = instance.method(1, 2)
        self.assertEqual(result, 4, "Method should return the sum of the two arguments and the counter")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should have one result")
        self.assertTrue(4 in list(DataSummariesCache.cached_results.values()), "Result should be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter['method'], 1)

        # Repeated call
        result = instance.method(1, 2)
        self.assertEqual(result, 4, "Method should return the cached result")
        self.assertEqual(len(DataSummariesCache.cached_results), 1, "Cache should still have one result")
        self.assertTrue(4 in list(DataSummariesCache.cached_results.values()), "Result should still be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter['method'], 2)

        # Call with different instance
        another_instance = TestClass()
        result = another_instance.method(1, 2)
        self.assertEqual(result, 4,
                         "Method should return the sum of the two arguments and the counter (from new instance)")
        self.assertEqual(len(DataSummariesCache.cached_results), 2, "Cache should have two results")
        self.assertTrue(4 in list(DataSummariesCache.cached_results.values()), "Both results should be cached")
        # pylint: disable=protected-access
        self.assertEqual(DataSummariesCache._hit_counter['method'], 3)
