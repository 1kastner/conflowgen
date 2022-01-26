import logging
import math
from typing import Dict, Any


logger = logging.getLogger("conflowgen")


def normalize_nested_distribution(distributions: Dict[Any, Dict[Any, float]]) -> Dict[Any, Dict[Any, float]]:
    normalized_distributions = {}
    for first_key, distribution in distributions.items():
        second_keys, fractions = zip(*distribution.items())
        sum_of_fractions = sum(fractions)
        if not math.isclose(sum_of_fractions, 1):
            logger.debug(f"Sum of fractions was not 1 for '{first_key}' and was automatically normalized.")
            fractions = [fraction / sum_of_fractions for fraction in fractions]
            for fraction in fractions:
                assert fraction >= 0
        normalized_distributions[first_key] = dict(zip(second_keys, fractions))
    return normalized_distributions
