from __future__ import annotations

import math
import random
from typing import Dict

import numpy as np


class SamplerExhaustedException(Exception):
    """No more samples can be sampled from the sampler"""
    pass


class DistributionApproximator:

    random_seed = 1

    def __init__(self, number_instances_per_category: Dict[any, int]) -> None:
        """
        Args:
            number_instances_per_category: For each key (category) the number of instances to draw is given
        """
        self.seeded_random = random.Random(x=self.random_seed)
        self.target_distribution = np.array(
            list(number_instances_per_category.values()),
            dtype=np.int64
        )
        self.number_categories = len(self.target_distribution)
        self.already_sampled = np.array([0 for _ in range(self.number_categories)])
        self.categories = list(number_instances_per_category.keys())

    @classmethod
    def from_distribution(
            cls,
            distribution: Dict[any, float],
            number_items: int
    ) -> DistributionApproximator:
        assert math.isclose(sum(distribution.values()), 1, abs_tol=.001), \
            f"All probabilities must sum to 1, but you only achieved {sum(distribution.values())}"

        # Approach the distribution by estimating the number of instances per category
        probability_based_instance_estimation = {
            category: int(round(probability * number_items))
            for (category, probability) in distribution.items()
        }

        # Due to rounding issues, the number of instances that have a category assigned is not equal to `number_items`
        # Thus, we need to fill the missing items by randomly drawing some of them.
        number_items_in_category_estimation = sum(probability_based_instance_estimation.values())
        if number_items_in_category_estimation < number_items:
            seeded_random = random.Random(x=cls.random_seed)
            items_lost_to_rounding = number_items - number_items_in_category_estimation
            randomly_chosen_categories = seeded_random.choices(
                population=list(distribution.keys()),
                weights=list(distribution.values()),
                k=items_lost_to_rounding
            )
            for category in randomly_chosen_categories:
                probability_based_instance_estimation[category] += 1
        distribution_approximator = DistributionApproximator(
            probability_based_instance_estimation
        )
        return distribution_approximator

    def sample(self) -> any:
        """
        Draws pseudo-random element so that the target distribution is approximated best
        """
        if self.already_sampled.sum() >= self.target_distribution.sum():
            raise SamplerExhaustedException(
                f"Only {self.target_distribution.sum()} draws are possible, "
                "you invoked `.sample()` too often")
        current_gap = self.target_distribution - self.already_sampled
        selected_category = self.seeded_random.choices(
            population=self.categories,
            weights=current_gap,
            k=1
        )[0]
        selected_category_index = self.categories.index(selected_category)
        self.already_sampled[selected_category_index] += 1
        return selected_category
