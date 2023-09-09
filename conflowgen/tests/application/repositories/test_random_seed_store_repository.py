import time
import unittest

import pytest

from conflowgen.application.models.random_seed_store import RandomSeedStore
from conflowgen.application.repositories.random_seed_store_repository import RandomSeedStoreRepository
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestRandomSeedStoreRepository(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            RandomSeedStore
        ])
        self.repository = RandomSeedStoreRepository()

    def test_get_empty_entry(self):
        with self.assertLogs('conflowgen', level='DEBUG') as context:
            random_seed = self.repository.get_random_seed("empty_entry", True)
        self.assertIsInstance(random_seed, int)
        self.assertEqual(len(context.output), 1)
        logged_message = context.output[0]
        self.assertRegex(logged_message, r"Randomly set seed \d+ for 'empty_entry'")

    def test_fix_existing_entry(self):
        seed = int(time.time())
        with self.assertLogs('conflowgen', level='DEBUG') as context:
            self.repository.fix_random_seed("fix_seed", seed, True)
        self.assertEqual(len(context.output), 1)
        logged_message = context.output[0]
        self.assertRegex(logged_message, r"Set seed \d+ for 'fix_seed'")

    def test_reuse_existing_entry(self):
        seed = int(time.time())
        RandomSeedStore.create(
            name="reuse_existing",
            random_seed=seed,
            is_random=True
        )
        random_seed = self.repository.get_random_seed("reuse_existing", False)
        self.assertEqual(random_seed, seed)

    def test_fix_and_reuse_journey(self):
        for _ in range(10):
            seed = int(time.time())
            with self.assertLogs('conflowgen', level='DEBUG') as context:
                self.repository.fix_random_seed("fix_and_reuse", seed, True)
            self.assertEqual(len(context.output), 1)
            logged_message = context.output[0]
            self.assertRegex(logged_message, rf"Set seed {seed} for 'fix_and_reuse'")

            with self.assertLogs('conflowgen', level='DEBUG') as context:
                retrieved_seed = self.repository.get_random_seed("fix_and_reuse", True)
            self.assertEqual(len(context.output), 1)
            logged_message = context.output[0]
            self.assertRegex(
                logged_message,
                fr"Re-use seed {retrieved_seed} for 'fix_and_reuse'"
            )

            self.assertEqual(seed, retrieved_seed)
