"""
Check if mode of transportation is properly translated between application and database.
"""

import unittest

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.field_types.mode_of_transport import ModeOfTransportField


class TestModeOfTransportation(unittest.TestCase):
    """
    The actual ModeOfTransportField behavior is implemented in peewee.
    """

    def test_conversion_to_database_value(self):
        """When writing to the database, the enum is converted to a number"""
        truck_application_value = ModeOfTransport.truck
        truck_database_value = "truck"
        mode_of_transport_field = ModeOfTransportField()
        self.assertEqual(mode_of_transport_field.db_value(truck_application_value), truck_database_value)

    def test_conversion_to_application_value(self):
        """When reading from the database, the number is converted to the enum"""
        truck_application_value = ModeOfTransport.truck
        truck_database_value = "truck"
        mode_of_transport_field = ModeOfTransportField()
        self.assertEqual(mode_of_transport_field.python_value(truck_database_value), truck_application_value)
