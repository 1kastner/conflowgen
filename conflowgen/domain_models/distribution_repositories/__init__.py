import logging
import math
from typing import Dict, Any, Optional

logger = logging.getLogger("conflowgen")


def normalize_distribution_with_no_dependent_variable(
        distribution: Dict[Any, float],
        context: Optional[Any] = None
) -> Dict[Any, float]:
    keys, fractions = zip(*distribution.items())
    sum_of_fractions = sum(fractions)
    if not math.isclose(sum_of_fractions, 1):
        context_text = f"for '{context}' " if context else ""
        logger.debug(f"Sum of fractions was not 1 {context_text}and was automatically normalized.")
        fractions = [fraction / sum_of_fractions for fraction in fractions]
        for fraction in fractions:
            assert fraction >= 0
    normalized_distribution = dict(zip(keys, fractions))
    return normalized_distribution


def normalize_distribution_with_one_dependent_variable(
        distributions: Dict[Any, Dict[Any, float]]
) -> Dict[Any, Dict[Any, float]]:
    normalized_distributions = {}
    for first_level_key, second_level_distribution in distributions.items():
        normalized_second_level_distribution = normalize_distribution_with_no_dependent_variable(
            second_level_distribution, context=first_level_key
        )
        normalized_distributions[first_level_key] = normalized_second_level_distribution
    return normalized_distributions
