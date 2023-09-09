import logging
import random
import typing
import time

from unicodedata import name

from conflowgen.application.models.random_seed_store import RandomSeedStore


class RandomSeedStoreRepository:

    def __init__(self):
        self.logger = logging.getLogger("conflowgen")

    def get_random_seed(self, seed_name: str, log_loading_process: bool = False) -> float:
        random_seed: float
        random_seed_store = RandomSeedStore.get_or_none(
            RandomSeedStore.name == seed_name
        )
        if random_seed_store is not None:
            if random_seed_store.is_random:
                # there is a previous seed but we are told to overwrite it
                previous_seed = random_seed_store.random_seed
                random_seed = self._get_random_seed()
                random_seed_store.random_seed = random_seed
                random_seed_store.save()
                if log_loading_process:
                    self.logger.debug(f"Overwrite seed {previous_seed} with {random_seed} for '{seed_name}'")
                return random_seed
            else:
                # there is a previous seed and we should re-use it
                random_seed = random_seed_store.random_seed
                if log_loading_process:
                    self.logger.debug(f"Re-use seed {random_seed} for '{seed_name}'")
                return random_seed
        else:
            # there is no previous seed available, enter the current seed and return its value
            random_seed = self._get_random_seed()
            RandomSeedStore.create(
                name=seed_name,
                random_seed=random_seed,
                is_random=True
            )
            if log_loading_process:
                self.logger.debug(f"Randomly set seed {random_seed} for '{seed_name}'")
            return random_seed

    @staticmethod
    def _get_random_seed() -> int:
        return int(time.time())

    def fix_random_seed(
            self, seed_name: str, random_seed: typing.Optional[int], log_loading_process: bool = False
    ) -> None:
        if random_seed is None:
            random_seed = self._get_random_seed()
        random_seed_store = RandomSeedStore.get_or_none(
            RandomSeedStore.name == seed_name
        )
        if random_seed_store is None:
            random_seed_store = RandomSeedStore.create(
                name=seed_name,
                is_random=False,
                random_seed=random_seed
            )
        else:
            random_seed_store.random_seed = random_seed
        if log_loading_process:
            self.logger.debug(f"Set seed {random_seed} for '{seed_name}'")
        random_seed_store.save()


_random_seed_store_repository = RandomSeedStoreRepository()


def get_initialised_random_object(seed_name: str, log_loading_process: bool = True) -> random.Random:
    random_seed = RandomSeedStoreRepository().get_random_seed(seed_name, log_loading_process=log_loading_process)
    seeded_random = random.Random(x=random_seed)
    return seeded_random
