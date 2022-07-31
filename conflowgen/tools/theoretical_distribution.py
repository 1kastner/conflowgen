import abc
import math
from typing import Collection, Sequence

import numpy as np
import scipy.stats


class TheoreticalDistribution(abc.ABC):

    average: float
    minimum: float
    maximum: float

    def __init__(self, average: float, minimum: float, maximum: float):
        assert minimum < average < maximum, f"The assertion {minimum} < {average} < {maximum} failed."
        self.average = average
        self.minimum = minimum
        self.maximum = maximum

    @abc.abstractmethod
    def _get_probability_based_on_distribution(self, x: float) -> float:
        pass

    def get_probability(self, x: float) -> float:
        """

        Args:
            x: The element, on the same scale as average, variance, minimum, and maximum

        Returns:
            The probability that element x is drawn from this distribution

        """
        if not (self.minimum < x < self.maximum):
            return 0
        else:
            return self._get_probability_based_on_distribution(x)

    def get_probabilities(self, xs: Collection[float]) -> Collection[float]:
        return [self.get_probability(x) for x in xs]


class ClippedLogNormal(TheoreticalDistribution):

    variance: float

    def __init__(self, average: float, variance: float, minimum: float, maximum: float):
        super().__init__(
            average=average,
            minimum=minimum,
            maximum=maximum
        )
        self.variance = variance
        self._lognorm = self._get_scipy_lognorm()

    def _get_scipy_lognorm(self) -> "scipy.stats.rv_frozen":
        # See https://www.johndcook.com/blog/2022/02/24/find-log-normal-parameters/ for reference
        sigma2 = math.log(self.variance / self.average ** 2 + 1)
        mu = math.log(self.average) - sigma2 / 2

        scipy_shape = sigma2 ** 0.5
        scipy_scale = math.exp(mu)

        frozen_lognorm = scipy.stats.lognorm(s=scipy_shape, scale=scipy_scale)

        return frozen_lognorm

    def _get_probability_based_on_distribution(self, x) -> float:
        return self._lognorm.pdf(x)


def multiply_discretized_probability_densities(*probabilities: Collection[float]) -> Sequence[float]:
    assert len(set([len(p) for p in probabilities])) == 1, "All probability vectors have the same length"
    np_probs = [np.array(probs) for probs in probabilities]
    multiplied_probabilities = np.multiply(*np_probs)
    normalized_probabilities = multiplied_probabilities / multiplied_probabilities.sum()
    assert abs(sum(normalized_probabilities) - 1) < 0.001
    return normalized_probabilities
