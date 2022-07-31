"""
Check if container weights can be properly seeded.
"""
import datetime
import unittest

from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository, InvalidTimeRangeException, \
    DuplicatedContainerFlowGenerationPropertiesEntryException, MinimumNotStrictlySmallerThanMaximumException
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowGenerationProperties(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            ContainerFlowGenerationProperties
        ])
        self.repository = ContainerFlowGenerationPropertiesRepository()

    def test_get_default_values(self):
        properties = self.repository.get_container_flow_generation_properties()
        self.assertIsNone(properties.name)
        self.assertIsNone(properties.start_date)
        self.assertIsNone(properties.end_date)
        self.assertLessEqual(
            properties.generated_at - datetime.datetime.now(),
            datetime.timedelta(minutes=1)
        )
        self.assertLessEqual(
            properties.last_updated_at - datetime.datetime.now(),
            datetime.timedelta(minutes=1)
        )

    def test_properties_creation_behavior_with_get(self):
        all_properties_first = list(ContainerFlowGenerationProperties.select())
        self.assertEqual(all_properties_first, [])
        properties_1 = self.repository.get_container_flow_generation_properties()
        self.assertIsInstance(properties_1, ContainerFlowGenerationProperties)
        all_properties_second = list(ContainerFlowGenerationProperties.select())
        self.assertEqual(len(all_properties_second), 1)
        properties_2 = self.repository.get_container_flow_generation_properties()
        self.assertIsInstance(properties_2, ContainerFlowGenerationProperties)
        all_properties_third = list(ContainerFlowGenerationProperties.select())
        self.assertEqual(len(all_properties_third), 1)

    def test_set_values(self):
        properties = self.repository.get_container_flow_generation_properties()
        name = "Test"
        properties.name = name
        start_date = datetime.datetime.now()
        properties.start_date = start_date
        end_date = datetime.datetime.now() + datetime.timedelta(days=5)
        properties.end_date = end_date
        self.repository.set_container_flow_generation_properties(properties)
        loaded_properties = self.repository.get_container_flow_generation_properties()
        self.assertEqual(loaded_properties.name, name)
        self.assertEqual(loaded_properties.start_date, start_date.date())
        self.assertEqual(loaded_properties.end_date, end_date.date())
        self.assertLessEqual(
            properties.generated_at - datetime.datetime.now(),
            datetime.timedelta(minutes=1)
        )
        self.assertLessEqual(
            properties.last_updated_at - datetime.datetime.now(),
            datetime.timedelta(minutes=1)
        )

    def test_broken_properties__end_date_too_early(self):
        with self.assertRaises(InvalidTimeRangeException):
            self.repository.set_container_flow_generation_properties(
                ContainerFlowGenerationProperties.create(
                    start_date=datetime.datetime.now(),
                    end_date=datetime.datetime.now() - datetime.timedelta(days=5)
                )
            )

    def test_broken_properties__double_entry_in_database(self):
        ContainerFlowGenerationProperties.create(
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() - datetime.timedelta(days=5)
        ).save()
        ContainerFlowGenerationProperties.create(
            start_date=datetime.datetime.now(),
            end_date=datetime.datetime.now() - datetime.timedelta(days=5)
        ).save()
        with self.assertRaises(DuplicatedContainerFlowGenerationPropertiesEntryException):
            self.repository.get_container_flow_generation_properties()

    def test_set_values_on_old_instance(self):
        """
        If not set, changes at the old instance should not have any effect.
        """
        properties = self.repository.get_container_flow_generation_properties()
        name_old = "Test old"
        properties.name = name_old
        start_date_old = (datetime.datetime.now() - datetime.timedelta(days=5)).date()
        properties.start_date = start_date_old
        end_date_old = (datetime.datetime.now() - datetime.timedelta(days=2)).date()
        properties.end_date = end_date_old
        self.repository.set_container_flow_generation_properties(properties)

        name_new = "Test new"
        properties.name = name_new
        start_date_new = (datetime.datetime.now() + datetime.timedelta(days=2)).date()
        properties.start_date = start_date_new
        end_date_new = (datetime.datetime.now() + datetime.timedelta(days=5)).date()
        properties.end_date = end_date_new

        loaded_properties = self.repository.get_container_flow_generation_properties()
        self.assertEqual(loaded_properties.name, name_old)
        self.assertEqual(loaded_properties.start_date, start_date_old)
        self.assertEqual(loaded_properties.end_date, end_date_old)

    def test_set_values_twice(self):
        properties_old = self.repository.get_container_flow_generation_properties()
        name_old = "Test old"
        properties_old.name = name_old
        start_date_old = (datetime.datetime.now() - datetime.timedelta(days=5)).date()
        properties_old.start_date = start_date_old
        end_date_old = (datetime.datetime.now() - datetime.timedelta(days=2)).date()
        properties_old.end_date = end_date_old
        self.repository.set_container_flow_generation_properties(properties_old)

        properties_new = self.repository.get_container_flow_generation_properties()
        name_new = "Test new"
        properties_new.name = name_new
        start_date_new = (datetime.datetime.now() + datetime.timedelta(days=2)).date()
        properties_new.start_date = start_date_new
        end_date_new = (datetime.datetime.now() + datetime.timedelta(days=5)).date()
        properties_new.end_date = end_date_new
        self.repository.set_container_flow_generation_properties(properties_new)

        loaded_properties = self.repository.get_container_flow_generation_properties()
        self.assertEqual(loaded_properties.name, name_new)
        self.assertEqual(loaded_properties.start_date, start_date_new)
        self.assertEqual(loaded_properties.end_date, end_date_new)
